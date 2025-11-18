import paho.mqtt.client as mqtt
import json
import logging
from datetime import datetime
import config
from database import Database

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

db = Database()

# Callback when connected to MQTT broker
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logger.info("✅ Connected to MQTT broker")

        for topic in config.MQTT_TOPICS:
            client.subscribe(topic)
        logger.info(f"📡 Subscribed to: {topic}")

    else:
        logger.error(f"❌ Connection failed with code {rc}")

# Callback when message received
def on_message(client, userdata, msg):
    try:
        
        topic = msg.topic
        payload = msg.payload.decode('utf-8')
        
        logger.debug(f"Received: {topic} -> {payload}")
        
        # Handle different topic types
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
    # Extract sensor name from topic
    # "sensors/temperature" -> "temperature"
    sensor_name = topic.split('/')[-1]
    # Parse value - handle both JSON and plain number
    try:
        # Try JSON first
        data = json.loads(payload)
        value = data.get('value')
        unit = data.get('unit', None)
    except (json.JSONDecodeError, AttributeError):
        # Plain number
        try:
            value = float(payload)
            unit = None
        except ValueError:
            logger.error(f"Could not parse value: {payload}")
            return

# Save to database
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
            # Could save to system_status table here
        
        elif topic == 'system/status':
            status = data.get('status')
            logger.info(f"⚙️  System status: {status}")
            
    except Exception as e:
        logger.error(f"Error handling system data: {e}")

# Main program
def main():
    """Main entry point"""
    logger.info("=" * 50)
    logger.info("MQTT Listener Starting")
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
        logger.info(f"Connecting to {config.MQTT_BROKER}:{config.MQTT_PORT}...")
    except Exception as e:
        logger.error(f"Failed to connect: {e}")
        return
    
    try:
        logger.info("Listening for messages... (Press Ctrl+C to stop)")
        client.loop_forever()

    except KeyboardInterrupt:
        logger.info("\n🛑 Stopping listener...")
        client.disconnect()
        db.close()
        logger.info("✅ Disconnected cleanly")

if __name__ == '__main__':
    main()