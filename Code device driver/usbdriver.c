#include <linux/kernel.h>
#include <linux/module.h>
#include <linux/usb.h>


#define IS_NEW_METHOD_USED  ( 1 )
#define USB_VENDOR_ID       ( 0x0c45 )      //USB device's vendor ID
#define USB_PRODUCT_ID      ( 0x7644 )      //USB device's product ID


#define PRINT_USB_INTERFACE_DESCRIPTOR( i )                         \
{                                                                   \
    pr_info("USB_INTERFACE_DESCRIPTOR:\n");                         \
    pr_info("-----------------------------\n");                     \
    pr_info("bLength: 0x%x\n", i.bLength);                          \
    pr_info("bDescriptorType: 0x%x\n", i.bDescriptorType);          \
    pr_info("bInterfaceNumber: 0x%x\n", i.bInterfaceNumber);        \
    pr_info("bAlternateSetting: 0x%x\n", i.bAlternateSetting);      \
    pr_info("bNumEndpoints: 0x%x\n", i.bNumEndpoints);              \
    pr_info("bInterfaceClass: 0x%x\n", i.bInterfaceClass);          \
    pr_info("bInterfaceSubClass: 0x%x\n", i.bInterfaceSubClass);    \
    pr_info("bInterfaceProtocol: 0x%x\n", i.bInterfaceProtocol);    \
    pr_info("iInterface: 0x%x\n", i.iInterface);                    \
    pr_info("\n");                                                  \
}
#define PRINT_USB_ENDPOINT_DESCRIPTOR( e )                          \
{                                                                   \
    pr_info("USB_ENDPOINT_DESCRIPTOR:\n");                          \
    pr_info("------------------------\n");                          \
    pr_info("bLength: 0x%x\n", e.bLength);                          \
    pr_info("bDescriptorType: 0x%x\n", e.bDescriptorType);          \
    pr_info("bEndPointAddress: 0x%x\n", e.bEndpointAddress);        \
    pr_info("bmAttributes: 0x%x\n", e.bmAttributes);                \
    pr_info("wMaxPacketSize: 0x%x\n", e.wMaxPacketSize);            \
    pr_info("bInterval: 0x%x\n", e.bInterval);                      \
    pr_info("\n");                                                  \
}
/*
** This function will be called when USB device is inserted.
*/
static int etx_usb_probe(struct usb_interface *interface,
                        const struct usb_device_id *id)
{
    dev_info(&interface->dev, "USB Driver Probed: Vendor ID : 0x%02x,\t"
             "Product ID : 0x%02x\n", id->idVendor, id->idProduct);
    return 0;  
}


static void etx_usb_disconnect(struct usb_interface *interface)
{
    dev_info(&interface->dev, "USB Driver Disconnected\n");
}

const struct usb_device_id etx_usb_table[] = {
    { USB_DEVICE( USB_VENDOR_ID, USB_PRODUCT_ID ) },    
    { } 
};

MODULE_DEVICE_TABLE(usb, etx_usb_table);
static struct usb_driver etx_usb_driver = {
    .name       = "USB driver",
    .probe      = etx_usb_probe,
    .disconnect = etx_usb_disconnect,
    .id_table   = etx_usb_table,
};
#if ( IS_NEW_METHOD_USED == 0 )

module_usb_driver(etx_usb_driver);

#else
static int __init etx_usb_init(void)
{
    //register the USB device
    return usb_register(&etx_usb_driver);
}
static void __exit etx_usb_exit(void)
{
    //deregister the USB device
    usb_deregister(&etx_usb_driver);
}
module_init(etx_usb_init);
module_exit(etx_usb_exit);
#endif
MODULE_LICENSE("GPL");
MODULE_AUTHOR("Test usb driver");
MODULE_DESCRIPTION("Simple usb driver for check plugin usb");
MODULE_VERSION("1");
