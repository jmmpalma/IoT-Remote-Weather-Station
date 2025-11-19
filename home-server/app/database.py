import psycopg2
from psycopg2 import pool
from datetime import datetime, timedelta
import logging
import config

logger = logging.getLogger(__name__)

class Database:
    """Handles all database operations"""
    
    def __init__(self):
        """Initialize connection pool - Creates 1 to 10 DB connections that will be used as needed"""
        try:
            self.pool = psycopg2.pool.SimpleConnectionPool(
                1,  # Minimum connections
                10,  # Maximum connections
                host=config.DB_HOST,
                port=config.DB_PORT,
                database=config.DB_NAME,
                user=config.DB_USER,
                password=config.DB_PASSWORD
            )
            logger.info("Database connection pool created")
        except Exception as e:
            logger.error(f"Failed to create connection pool: {e}")
            raise
    
    def get_connection(self):
        """Get a connection from pool"""
        return self.pool.getconn()
    
    def return_connection(self, conn):
        """Return connection to pool"""
        self.pool.putconn(conn)
    
    def save_sensor_reading(self, sensor_name, value, unit=None):
        """
        Save a sensor reading to database
        
        Args:
            sensor_name: Name of the sensor (e.g., 'temperature')
            value: Reading value (float)
            unit: Optional unit (e.g., 'celsius')
        """
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                """
                INSERT INTO sensor_readings (sensor_name, value, unit)
                VALUES (%s, %s, %s)
                """,
                (sensor_name, value, unit)
            )
            
            conn.commit()
            cursor.close()
            logger.debug(f"Saved: {sensor_name} = {value}")
            
        except Exception as e:
            logger.error(f"Error saving reading: {e}")
            if conn:
                conn.rollback()
        finally:
            if conn:
                self.return_connection(conn)
    
    def get_latest_reading(self, sensor_name):
        """
        Get the most recent reading for a sensor
        
        Args:
            sensor_name: Name of the sensor
            
        Returns:
            dict with 'timestamp', 'value', 'unit' or None if no data
        """
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                """
                SELECT timestamp, value, unit
                FROM sensor_readings
                WHERE sensor_name = %s
                ORDER BY timestamp DESC
                LIMIT 1
                """,
                (sensor_name,)
            )
            
            row = cursor.fetchone()
            cursor.close()
            
            if row:
                return {
                    'timestamp': row[0].isoformat(),
                    'value': float(row[1]),
                    'unit': row[2]
                }
            return None
            
        except Exception as e:
            logger.error(f"Error getting latest reading: {e}")
            return None
        finally:
            if conn:
                self.return_connection(conn)
    
    def get_recent_readings(self, sensor_name=None, hours=24):
        """
        Get recent sensor readings
        
        Args:
            sensor_name: Optional sensor name filter
            hours: How many hours back to query
            
        Returns:
            List of dicts with 'timestamp', 'sensor', 'value', 'unit'
        """
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            if sensor_name:
                cursor.execute(
                    """
                    SELECT timestamp, sensor_name, value, unit
                    FROM sensor_readings
                    WHERE sensor_name = %s
                      AND timestamp > NOW() - INTERVAL '%s hours'
                    ORDER BY timestamp ASC
                    """,
                    (sensor_name, hours)
                )
            else:
                cursor.execute(
                    """
                    SELECT timestamp, sensor_name, value, unit
                    FROM sensor_readings
                    WHERE timestamp > NOW() - INTERVAL '%s hours'
                    ORDER BY timestamp ASC
                    """,
                    (hours,)
                )
            
            results = cursor.fetchall()
            cursor.close()
            
            return [
                {
                    'timestamp': row[0].isoformat(),
                    'sensor': row[1],
                    'value': float(row[2]),
                    'unit': row[3]
                }
                for row in results
            ]
            
        except Exception as e:
            logger.error(f"Error getting readings: {e}")
            return []
        finally:
            if conn:
                self.return_connection(conn)
    
    def save_image(self, filename, trigger='unknown'):
        """
        Save image metadata to database
        
        Args:
            filename: Image filename
            trigger: What triggered the capture (e.g., 'motion')
        """
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                """
                INSERT INTO images (filename, trigger)
                VALUES (%s, %s)
                """,
                (filename, trigger)
            )
            
            conn.commit()
            cursor.close()
            logger.info(f"Saved image metadata: {filename}")
            
        except Exception as e:
            logger.error(f"Error saving image: {e}")
            if conn:
                conn.rollback()
        finally:
            if conn:
                self.return_connection(conn)
    
    def get_recent_images(self, limit=20):
        """
        Get recent image metadata
        
        Args:
            limit: Maximum number of images to return
            
        Returns:
            List of dicts with image info
        """
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                """
                SELECT timestamp, filename, trigger
                FROM images
                ORDER BY timestamp DESC
                LIMIT %s
                """,
                (limit,)
            )
            
            results = cursor.fetchall()
            cursor.close()
            
            return [
                {
                    'timestamp': row[0].isoformat(),
                    'filename': row[1],
                    'trigger': row[2]
                }
                for row in results
            ]
            
        except Exception as e:
            logger.error(f"Error getting images: {e}")
            return []
        finally:
            if conn:
                self.return_connection(conn)
    
    def cleanup_old_data(self):
        """Remove old data to save space"""
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                """
                DELETE FROM sensor_readings
                WHERE timestamp < NOW() - INTERVAL '%s days'
                """,
                (config.KEEP_READINGS_DAYS,)
            )
            readings_deleted = cursor.rowcount
            
            cursor.execute(
                """
                DELETE FROM images
                WHERE timestamp < NOW() - INTERVAL '%s days'
                """,
                (config.KEEP_IMAGES_DAYS,)
            )
            images_deleted = cursor.rowcount
            
            conn.commit()
            cursor.close()
            
            logger.info(f"Cleanup: {readings_deleted} readings, {images_deleted} images deleted")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
            if conn:
                conn.rollback()
        finally:
            if conn:
                self.return_connection(conn)
    
    def close(self):
        """Close all connections in pool"""
        if self.pool:
            self.pool.closeall()
            logger.info("Database connections closed")


if __name__ == '__main__':
    print("Testing database module...")
    
    db = Database()
    
    print("Saving test reading...")
    db.save_sensor_reading('test_sensor', 42.0, 'test_unit')
    
    print("Getting latest reading...")
    latest = db.get_latest_reading('test_sensor')
    print(f"Latest: {latest}")
    
    print("Getting recent readings...")
    recent = db.get_recent_readings('test_sensor', hours=1)
    print(f"Found {len(recent)} readings")
    
    db.close()
    print("Database test complete!")