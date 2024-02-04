import argparse
class Get_Args:
    def __init__(self):
        parser = argparse.ArgumentParser(description='Execute a Python file.')
        # parser.add_argument('-app', '--app', required=True, help='UDID argument description')
        parser.add_argument('-udid', '--udid', required=True, help='UDID argument description',default=None)
        parser.add_argument('-AppiumUrl', '--AppiumUrl', required=True, help='UDID argument description',default=None)
        parser.add_argument('-PlatformName', '--PlatformName', required=True, help='UDID argument description',default=None)
        # parser.add_argument('-user_capture', '--user_capture', required=True, help='UDID argument description')
        self.args = parser.parse_args()
        self.udid = self.args.udid
        self.AppiumUrl = self.args.AppiumUrl
        self.PlatformName = self.args.PlatformName
        # self.user_capture = self.args.user_capture
    def get_data(self):
        return self.udid,self.AppiumUrl,self.PlatformName