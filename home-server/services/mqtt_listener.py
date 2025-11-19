import sys
import os

# Add parent directory to path so we can import from app/
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import paho.mqtt.client as mqtt
import json
import logging
from datetime import datetime
import config
from database import Database

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(config.LOG_DIR, 'mqtt_listener.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Create database connection
db = Database()

def on_connect(client, userdata, flags, rc):
    """Called when connected to MQTT broker"""
    if rc == 0:
        logger.info("✅ Connected to MQTT broker")
        
        for topic in config.MQTT_TOPICS:
            client.subscribe(topic)
            logger.info(f"📡 Subscribed to: {topic}")
    else:
        logger.error(f"❌ Connection failed with code {rc}")

def on_message(client, userdata, msg):
    """Called when message received"""
    try:
        topic = msg.topic
        payload = msg.payload.decode('utf-8')
        
        logger.debug(f"Received: {topic} -> {payload}")
        
        if topic.startswith('sensors/'):
            handle_sensor_data(topic, payload)
        elif topic.startswith('camera/'):
            handle_camera_data(topic, payload)
        elif topic.startswith('system/'):
            handle_system_data(topic, payload)
        else:
            logger.warning(f"Unknown topic: {topic}")
            
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        import traceback
        traceback.print_exc()

def handle_sensor_data(topic, payload):
    """Process sensor data messages"""
    sensor_name = topic.split('/')[-1]
    
    try:
        data = json.loads(payload)
        value = data.get('value')
        unit = data.get('unit', None)
    except (json.JSONDecodeError, AttributeError):
        try:
            value = float(payload)
            unit = None
        except ValueError:
            logger.error(f"Could not parse value: {payload}")
            return
    
    db.save_sensor_reading(sensor_name, value, unit)
    logger.info(f"💾 Saved: {sensor_name} = {value} {unit if unit else ''}")

def handle_camera_data(topic, payload):
    """Process camera-related messages"""
    if topic == 'camera/motion':
        try:
            data = json.loads(payload)
            filename = data.get('filename')
            trigger = data.get('trigger', 'motion')
            
            if filename:
                db.save_image(filename, trigger)
                logger.info(f"📷 Image captured: {filename}")
        except Exception as e:
            logger.error(f"Error handling camera data: {e}")

def handle_system_data(topic, payload):
    """Process system status messages"""
    try:
        data = json.loads(payload)
        
        if topic == 'system/battery':
            voltage = data.get('voltage')
            percent = data.get('percent')
            logger.info(f"🔋 Battery: {percent}% ({voltage}V)")
            
        elif topic == 'system/status':
            status = data.get('status')
            logger.info(f"⚙️  System status: {status}")
            
    except Exception as e:
        logger.error(f"Error handling system data: {e}")

def main():
    """Main entry point"""
    logger.info("=" * 50)
    logger.info("MQTT Listener Service Starting")
    logger.info("=" * 50)
    logger.info(f"Broker: {config.MQTT_BROKER}:{config.MQTT_PORT}")
    logger.info(f"Topics: {', '.join(config.MQTT_TOPICS)}")
    logger.info("=" * 50)
    
    client = mqtt.Client()
    client.username_pw_set(config.MQTT_USERNAME, config.MQTT_PASSWORD)
    client.on_connect = on_connect
    client.on_message = on_message
    
    try:
        client.connect(config.MQTT_BROKER, config.MQTT_PORT, 60)
        logger.info("Connected successfully")
    except Exception as e:
        logger.error(f"Failed to connect: {e}")
        return
    
    try:
        logger.info("Listening for messages... (Press Ctrl+C to stop)\n")
        client.loop_forever()
    except KeyboardInterrupt:
        logger.info("\n🛑 Stopping listener...")
        client.disconnect()
        db.close()
        logger.info("✅ Disconnected cleanly")

if __name__ == '__main__':
    main()