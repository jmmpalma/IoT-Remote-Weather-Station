import psycopg2
from psycopg2 import pool
from datetime import datetime, timedelta
import logging
import config 

# Setting up a logger so we can see database events in the console
logger = logging.getLogger(__name__)

class Database:
    """
    This class acts as the bridge between Python and PostgreSQL.
    Instead of opening a new connection every single time a sensor sends data 
    (which is slow), we create a 'Pool' of connections and reuse them."""
    
    def __init__(self):
        """
        The Constructor: Runs once when you type 'db = Database()'
        """
        try:
            # We create a 'SimpleConnectionPool'. 
            # 1: Minimum number of connections to keep open.
            # 5: Maximum connections allowed (prevents crashing the VM RAM).
            self.pool = psycopg2.pool.SimpleConnectionPool(
                1, 5,
                host=config.DB_HOST,
                port=config.DB_PORT,
                database=config.DB_NAME,
                user=config.DB_USER,
                password=config.DB_PASSWORD
            )
            logger.info("Database connection pool created")
        except Exception as e:
            logger.error(f"Failed to create connection pool: {e}")
            raise # Stops the program if the database can't be reached
    
    def get_connection(self):
        return self.pool.getconn() #Gets a connection from the 5 existing in the pool
    
    def return_connection(self, conn):
        self.pool.putconn(conn) #After the operations are done, return the connection to the pool
    
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
            # 1. Borrow a connection from the pool
            conn = self.get_connection()
            # 2. Create a 'cursor' (the tool that actually writes the SQL)
            cursor = conn.cursor()
            # 3. Define the SQL command. 
            # %s is used as placeholder to prevent 'SQL Injection' (hacking).
            sql = "INSERT INTO sensor_readings (sensor_name, value, unit) VALUES (%s, %s, %s)"               
            
            # 4. Execute the command with our data
            cursor.execute(sql,(sensor_name, value, unit))

            # 5. COMMIT: This actually saves the data permanently. 
            # If there isn't a commit, the data disappears when the script stops!
            conn.commit()
            cursor.close()
            logger.debug(f"Saved: {sensor_name} = {value}")
            
        except Exception as e:
            logger.error(f"Error saving reading: {e}")
            # 6. ROLLBACK: If there was an error, undo everything in this transaction
            # so the database doesn't get corrupted or stuck.
            if conn:
                conn.rollback()
        finally:
            # 7. ALWAYS return the connection, even if the code crashed.
            if conn: self.return_connection(conn)
    
    def get_latest_reading(self, sensor_name):
        """
        Get the most recent reading for a sensor, used to display current values.
        Args:
            sensor_name: Name of the sensor
        Returns:
            dict with 'timestamp', 'value', 'unit' or None if no data
        """
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            sql = "SELECT timestamp, value, unit FROM sensor_readings WHERE sensor_name = %s ORDER BY timestamp DESC LIMIT 1"

            cursor.execute(sql,(sensor_name,))
            
            row = cursor.fetchone() # Fetch the single row result
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
    
    def close(self):
        #Close all connections in the pool
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