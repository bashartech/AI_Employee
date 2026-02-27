# Start Odoo Container Commands

# 1. Start the container
docker start oddo

# 2. Check if it's running
docker ps | grep oddo

# 3. View container logs (if needed)
docker logs oddo

# 4. Follow logs in real-time
docker logs -f oddo

# 5. Stop the container (when needed)
docker stop oddo

# 6. Restart the container
docker restart oddo

# Access Odoo:
# Open browser: http://localhost:8069
