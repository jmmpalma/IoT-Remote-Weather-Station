import sys
import argparse

def main():
    parser = argparse.ArgumentParser(description='IoT Home Server')
    parser.add_argument('service', choices=['listener', 'web', 'test'], 
                       help='Which service to run')
    
    args = parser.parse_args()
    
    if args.service == 'listener':
        from services.mqtt_listener import main as listener_main
        listener_main()
    elif args.service == 'web':
        from services.web_server import main as web_main
        web_main()

if __name__ == '__main__':
    main()