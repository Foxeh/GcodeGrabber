import Adafruit_BBIO.GPIO as GPIO
import dbus
import gobject
import commands,os,sys,random
import time

class DeviceAddedListener:
    
    """ lights
    GPIO.setup("P8_15", GPIO.OUT)
    GPIO.setup("P8_17", GPIO.OUT)
    GPIO.setup("P8_19", GPIO.OUT)

    GPIO.output("P8_15", GPIO.HIGH)
    """
    
    def __init__(self):
        
        self.bus = dbus.SystemBus()
        self.hal_manager_obj = self.bus.get_object("org.freedesktop.Hal", "/org/freedesktop/Hal/Manager")
        self.hal_manager = dbus.Interface(self.hal_manager_obj, "org.freedesktop.Hal.Manager")
        self.hal_manager.connect_to_signal("DeviceAdded", self._filter)
        self.hal_manager.connect_to_signal("DeviceRemoved", self._removal)

    def _filter(self, udi):
        
        device_obj = self.bus.get_object ("org.freedesktop.Hal", udi)
        device = dbus.Interface(device_obj, "org.freedesktop.Hal.Device")

        if device.QueryCapability("volume"):
            
            self.usb = True
            return self.do_something(device)

    def _removal(self, udi):

        if self.usb:
            
            """ lights
            GPIO.output("P8_15", GPIO.LOW)
            GPIO.output("P8_19", GPIO.HIGH)
            """
            
            if self.mounted:
                result = commands.getstatusoutput('sudo umount -f /dev/sda1')
                result = commands.getstatusoutput('sudo rm -rf %s' % (self.mount_dir))
                print "Device Removed."

            else:
                print "Device removed, something was wrong with it."
                
            self.mounted = False
            self.usb = False
            
            time.sleep(1)
            
            """ lights
            GPIO.output("P8_19", GPIO.LOW)
            GPIO.output("P8_15", GPIO.HIGH)
            """
            
            print "Ready"
            
    def do_something(self, volume):
        
        """ lights
        GPIO.output("P8_15", GPIO.LOW)
        GPIO.output("P8_17", GPIO.HIGH)
        """
        
        self.device_file = volume.GetProperty("block.device")
        self.label = volume.GetProperty("volume.label")
        self.fstype = volume.GetProperty("volume.fstype")
        self.mounted = volume.GetProperty("volume.is_mounted")
        self.mount_point = volume.GetProperty("volume.mount_point")
        self.uuid = volume.GetProperty("volume.uuid")                                   
        
        try:
            size = volume.GetProperty("volume.size")
        except:
            size = 0
                                                  
        print "New storage device detected:"
        print "  Device File: %s" % self.device_file
        print "  UUID: %s" % self.uuid
        print "  Label: %s" % self.label
        print "  Fstype: %s" % self.fstype
        print "  Size: %s (%.2fGB)" % (size, float(size) / 1024**3)

        time.sleep(1)
        
        if ' ' in self.label:
            name = self.label.split(' ')
            self.label = name[0] + "\ " + name[1]
        
        self.mount_dir = "/mnt/" + self.label
        mkdir = 'sudo mkdir %s' % (self.mount_dir)
        mount = 'sudo mount -t %s /dev/sda1 %s' % (self.fstype, self.mount_dir)
        print 'Mounting Device: %s (%s)' % (self.label, self.mount_dir)                   
                                                  
        if not os.path.exists(self.mount_dir):
            result = commands.getstatusoutput(mkdir)

            if result[0] != 0:
                
                """ lights
                GPIO.output("P8_17", GPIO.LOW)
                GPIO.output("P8_19", GPIO.HIGH)
                """
                
                print 'dir creation failed, aborting USB mount.'
                time.sleep(2)

            else:
                result = commands.getstatusoutput(mount)
                self.mounted = True

                remove = "sudo rm ~ctf-scada/etchasketch/files/*"
                result = commands.getstatusoutput(remove)
                copy = "sudo cp /mnt/" + self.label + "/*.gcode /tmp/gcode/"
                result = commands.getstatusoutput(copy)

                if result[0] != 0:
                    
                    """ lights
                    GPIO.output("P8_17", GPIO.LOW)
                    GPIO.output("P8_19", GPIO.HIGH)
                    """
                    
                    print 'Failed to copy Gcode...'
                    time.sleep(2)
                    
        else:
            
            """ lights
            GPIO.output("P8_17", GPIO.LOW)
            GPIO.output("P8_19", GPIO.HIGH)
            """
            
            print 'Unclean mount directory, please clean up.'
            time.sleep(2)

        result = commands.getstatusoutput('sudo umount -f /dev/sda1')
        result = commands.getstatusoutput('sudo rm -rf %s' % (self.mount_dir))
        
        time.sleep(1)
        
        """ lights
        GPIO.output("P8_17", GPIO.LOW)
        GPIO.output("P8_19", GPIO.LOW)
        GPIO.output("P8_15", GPIO.HIGH)
        time.sleep(.25)
        GPIO.output("P8_15", GPIO.LOW)
        time.sleep(.25)
        GPIO.output("P8_15", GPIO.HIGH)
        """
        
        print "Jobs Done."
        
if __name__ == '__main__':
    
    from dbus.mainloop.glib import DBusGMainLoop
    DBusGMainLoop(set_as_default=True)
    loop = gobject.MainLoop()
    DeviceAddedListener()
    loop.run()