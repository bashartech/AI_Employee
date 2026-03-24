"""
Scheduler Database - SQLite for storing scheduled posts
Stores scheduled posts until it's time to create approval files
"""
import sqlite3
from datetime import datetime
from pathlib import Path

# Database location
DB_PATH = Path(__file__).parent.parent / "scheduled_posts.db"


def init_db():
    """Initialize database with tables"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Scheduled posts table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS scheduled_posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            platform TEXT NOT NULL,
            content TEXT NOT NULL,
            scheduled_time DATETIME NOT NULL,
            status TEXT DEFAULT 'pending',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            posted_at DATETIME,
            error_message TEXT,
            approval_file TEXT,
            hashtags TEXT,
            is_thread INTEGER DEFAULT 0
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Scheduler database initialized")
    return DB_PATH


def add_scheduled_post(platform, content, scheduled_time, hashtags=None, is_thread=False, approval_file=None):
    """
    Add a post to the schedule
    
    Args:
        platform: 'twitter' or 'facebook'
        content: Post content/text
        scheduled_time: datetime object when post should be created
        hashtags: Optional hashtags
        is_thread: For Twitter, whether it's a thread
        approval_file: Optional reference to original approval file
    
    Returns:
        post_id: ID of the scheduled post
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO scheduled_posts 
        (platform, content, scheduled_time, hashtags, is_thread, approval_file)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (platform, content, scheduled_time, hashtags, 1 if is_thread else 0, approval_file))
    
    post_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    print(f"✅ Scheduled {platform} post ID: {post_id} for {scheduled_time}")
    return post_id


def get_pending_posts():
    """
    Get all posts that should be processed now
    
    Returns:
        List of tuples: (id, platform, content, hashtags, is_thread, approval_file)
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, platform, content, hashtags, is_thread, approval_file 
        FROM scheduled_posts 
        WHERE status = 'pending' 
        AND scheduled_time <= ?
        ORDER BY scheduled_time ASC
    ''', (datetime.now().strftime('%Y-%m-%d %H:%M:%S'),))
    
    posts = cursor.fetchall()
    conn.close()
    
    return posts


def get_all_scheduled_posts(limit=50):
    """
    Get all scheduled posts (for dashboard display)
    
    Returns:
        List of dicts with all post information
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM scheduled_posts 
        ORDER BY scheduled_time DESC
        LIMIT ?
    ''', (limit,))
    
    posts = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return posts


def update_post_status(post_id, status, error_message=None, approval_file=None):
    """
    Update post status after processing
    
    Args:
        post_id: ID of the scheduled post
        status: 'pending', 'processed', 'failed'
        error_message: Error message if failed
        approval_file: Path to created approval file
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    if status == 'processed':
        cursor.execute('''
            UPDATE scheduled_posts 
            SET status = ?, posted_at = ?, approval_file = ?
            WHERE id = ?
        ''', (status, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), approval_file, post_id))
    else:  # failed
        cursor.execute('''
            UPDATE scheduled_posts 
            SET status = ?, error_message = ?, approval_file = ?
            WHERE id = ?
        ''', (status, error_message, approval_file, post_id))
    
    conn.commit()
    conn.close()
    
    print(f"✅ Updated post {post_id} status to: {status}")


def delete_scheduled_post(post_id):
    """Delete a scheduled post (e.g., if user cancels)"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM scheduled_posts WHERE id = ?', (post_id,))
    
    deleted = cursor.rowcount
    conn.commit()
    conn.close()
    
    return deleted > 0


def get_scheduled_post(post_id):
    """Get a specific scheduled post by ID"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM scheduled_posts WHERE id = ?', (post_id,))
    
    post = cursor.fetchone()
    conn.close()
    
    return dict(post) if post else None


# Test the database
if __name__ == "__main__":
    print("🧪 Testing Scheduler Database...")
    
    # Initialize
    db_path = init_db()
    print(f"📁 Database created at: {db_path}")
    
    # Test adding a post
    test_time = datetime.now()
    post_id = add_scheduled_post(
        platform='twitter',
        content='Test scheduled tweet',
        scheduled_time=test_time,
        hashtags='#test #scheduled'
    )
    
    # Test getting pending posts
    pending = get_pending_posts()
    print(f"📬 Pending posts: {len(pending)}")
    
    # Test getting all posts
    all_posts = get_all_scheduled_posts()
    print(f"📋 All posts: {len(all_posts)}")
    
    # Test updating status
    update_post_status(post_id, 'processed', approval_file='test_approval.md')
    
    # Test getting specific post
    post = get_scheduled_post(post_id)
    print(f"📄 Retrieved post: {post['content']}")
    
    print("\n✅ All database tests passed!")
