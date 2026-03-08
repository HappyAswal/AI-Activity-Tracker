"""
Categorization engine for mapping applications and window titles to activity categories.
"""

PRODUCTIVITY_KEYWORDS = [
    # Programming Languages & Frameworks
    'python', 'javascript', 'typescript', 'java', 'c++', 'c#', 'golang', 'rust', 'swift', 'kotlin',
    'react', 'angular', 'vue', 'node.js', 'express', 'django', 'flask', 'spring boot', 'nextjs', 'next.js',
    'html', 'css', 'sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'graphql', 'rest api',
    # Development Tools & Platforms
    'github', 'gitlab', 'bitbucket', 'docker', 'kubernetes', 'aws', 'azure', 'gcp', 'heroku', 'vercel',
    'postman', 'insomnia', 'figma', 'sketch', 'terminal', 'powershell', 'bash', 'ubuntu', 'linux', 'wsl',
    'jira', 'trello', 'confluence', 'linear', 'asana', 'monday', 'clickup',
    # Learning & Problem Solving
    'stackoverflow', 'stack overflow', 'leetcode', 'hackerrank', 'codechef', 'codeforces', 'cses',
    'geeksforgeeks', 'gfg', 'coursera', 'udemy', 'pluralsight', 'freecodecamp', 'edx', 'khan academy',
    'documentation', 'docs', 'tutorial', 'course', 'algorithm', 'data structure', 'learn', 'study',
    'mdn', 'w3schools', 'devdocs', 'api reference',
    # Core Productivity Apps & Editors
    'vscode', 'visual studio code', 'visual studio', 'pycharm', 'intellij', 'eclipse', 'android studio', 'xcode',
    'jupyter', 'sublime', 'atom', 'notepad++', 'vim', 'emacs', 'nano',
    'word', 'excel', 'powerpoint', 'notion', 'obsidian', 'evernote', 'onenote',
    'google docs', 'google sheets', 'google slides', 'google drive',
    # Research & Reading
    'research', 'paper', 'article', 'blog', 'medium', 'dev.to', 'hashnode',
    'pdf', 'ebook', 'book', 'reading',
    # General Tech & Work terms
    'programming', 'coding', 'web development', 'learning', 'frontend', 'backend', 'fullstack',
    'development', 'developer', 'engineer', 'software', 'project', 'work', 'meeting', 'presentation'
]

ENTERTAINMENT_KEYWORDS = [
    # Streaming & Video
    'youtube', 'netflix', 'spotify', 'apple music', 'soundcloud', 'twitch', 'hulu', 'prime video', 
    'disney', 'disney+', 'hbo', 'hbo max', 'crunchyroll', 'vimeo', 'dailymotion',
    'music', 'movie', 'film', 'video', 'anime', 'show', 'series', 'season', 'episode', 'stream', 'streaming',
    'podcast', 'listen', 'watch', 'watching', 'listening',
    # Gaming
    'steam', 'epic games', 'riot games', 'blizzard', 'ea', 'ubisoft', 'xbox', 'playstation', 'nintendo',
    'valorant', 'league of legends', 'lol', 'cs2', 'csgo', 'counter strike', 'dota', 'dota 2',
    'minecraft', 'roblox', 'fortnite', 'apex legends', 'overwatch', 'gta', 'fifa', 'call of duty',
    'gaming', 'game', 'play', 'playing', 'esports', 'gamer', 'gameplay',
    # Shopping & Leisure
    'amazon', 'ebay', 'flipkart', 'myntra', 'aliexpress', 'etsy', 'shopping', 'shop', 'buy', 'purchase',
    'sports', 'espn', 'cricbuzz', 'score', 'football', 'cricket', 'basketball', 'soccer', 'nfl', 'nba',
    'news', 'cnn', 'bbc', 'fox news', 'gossip', 'celebrity', 'entertainment',
    # Social browsing (not social media apps)
    'meme', 'funny', 'viral', 'trending', '9gag', 'imgur'
]

SOCIAL_MEDIA_KEYWORDS = [
    'instagram', 'twitter', 'x.com', 'facebook', 'tiktok', 'reddit',
    'snapchat', 'linkedin', 'pinterest', 'tumblr', 'mastodon',
    'social media', 'feed', 'timeline', 'post', 'tweet', 'reels', 'stories'
]

COMMUNICATION_KEYWORDS = [
    'slack', 'teams', 'microsoft teams', 'zoom', 'skype', 'google meet',
    'telegram', 'signal', 'messenger', 'whatsapp', 'discord',
    'email', 'gmail', 'outlook', 'mail', 'chat', 'message', 'call', 'video call'
]

def _match_keyword(text, keyword):
    """
    Match keyword with word boundary awareness to avoid false positives.
    E.g., 'book' won't match 'facebook', but will match 'ebook reader'
    """
    import re
    # For multi-word keywords, use simple substring match
    if ' ' in keyword:
        return keyword in text
    # For single words, use word boundary matching
    pattern = r'\b' + re.escape(keyword) + r'\b'
    return bool(re.search(pattern, text))

def categorize_activity(app_name, window_title):
    """
    Categorize an activity based on app name and window title.
    
    Args:
        app_name: The process/application name
        window_title: The window title text
        
    Returns:
        str: Category name (Productivity, Entertainment, Social Media, Communication, Other)
    """
    clean_app, clean_title = DataCleaner.clean(app_name, window_title)
    
    # Priority 0: Ignore meaningless generic window titles
    if not clean_app.strip() and not clean_title.strip():
        return "Other"
    if clean_title in ["new tab", "untitled", "blank"]:
        return "Other"
    
    # Priority 1: Check if the app name itself is a hard match
    # (e.g. Spotify -> Entertainment, Slack -> Communication)
    # Browsers and generic hosts will have empty clean_names, so they fall through.
    if any(_match_keyword(clean_app, keyword) for keyword in COMMUNICATION_KEYWORDS):
        return "Communication"
    if any(_match_keyword(clean_app, keyword) for keyword in ENTERTAINMENT_KEYWORDS):
        return "Entertainment"
    if any(_match_keyword(clean_app, keyword) for keyword in SOCIAL_MEDIA_KEYWORDS):
        return "Social Media"
    if any(_match_keyword(clean_app, keyword) for keyword in PRODUCTIVITY_KEYWORDS):
        return "Productivity"
        
    combined = f"{clean_app} {clean_title}".lower()
    
    # Priority 2: Smart categorization with context awareness
    # Use word boundary matching to avoid false positives
    has_productivity = any(_match_keyword(combined, keyword) for keyword in PRODUCTIVITY_KEYWORDS)
    has_entertainment = any(_match_keyword(combined, keyword) for keyword in ENTERTAINMENT_KEYWORDS)
    has_social = any(_match_keyword(combined, keyword) for keyword in SOCIAL_MEDIA_KEYWORDS)
    has_communication = any(_match_keyword(combined, keyword) for keyword in COMMUNICATION_KEYWORDS)
    
    # Special case: YouTube/video content - check if it's educational
    if 'youtube' in combined or 'video' in combined:
        educational_terms = [
            'tutorial', 'programming', 'coding', 'leetcode', 'algorithm', 
            'python', 'java', 'javascript', 'course', 'learn', 'how to',
            'documentation', 'guide', 'lesson', 'lecture', 'education'
        ]
        if any(_match_keyword(combined, term) for term in educational_terms):
            return "Productivity"
        elif has_entertainment:
            return "Entertainment"
    
    # Priority order: Productivity > Communication > Social Media > Entertainment > Other
    if has_productivity:
        return "Productivity"
    elif has_communication:
        return "Communication"
    elif has_social:
        return "Social Media"
    elif has_entertainment:
        return "Entertainment"
    else:
        return "Other"

class DataCleaner:
    """Sanitizes raw strings from psutil and pygetwindow."""
    
    import re
    
    PROCESS_MAP = {
        'idea64': 'intellij',
        'code': 'vscode',
        'msedge': 'browser',
        'chrome': 'browser',
        'firefox': 'browser',
        'brave': 'browser',
        'applicationframehost': 'ignore',
        'searchapp': 'ignore',
        'explorer': 'ignore'
    }
    
    @classmethod
    def clean_process_name(cls, app_name):
        """Standardizes process names and strips extensions."""
        if not app_name or app_name == "Unknown":
            return ""
            
        name = app_name.lower().strip()
        
        # Strip common extensions
        for ext in ['.exe', '.bin', '.app']:
            if name.endswith(ext):
                name = name[:-len(ext)]
                
        # Map cryptic names to standard concepts
        if name in cls.PROCESS_MAP:
            mapped = cls.PROCESS_MAP[name]
            if mapped == 'ignore' or mapped == 'browser':
                return "" # We don't want the process name to influence the outcome here
            return mapped
            
        return name

    @classmethod
    def clean_window_title(cls, title):
        """Removes generic suffixes and absolute paths from window titles."""
        if not title or title == "Unknown":
            return ""
            
        import re
        clean = title.lower().strip()
        
        # Strategy 0: Remove dynamic notification counts from start of title like "(1) " or "(172)"
        clean = re.sub(r'^\(\d+\)\s*', '', clean)
        
        # Strategy 1: Remove common browser suffixes (- Google Chrome, - Personal - Microsoft Edge)
        clean = re.sub(r'\s*-\s*[^-]*(chrome|edge|firefox|brave).*$', '', clean)
        
        # Strategy 1.5: Remove Edge's annoying "and X more pages" tab grouping suffix
        clean = re.sub(r'\s*and\s+\d+\s+more\s+pages.*$', '', clean)
        
        # Strategy 2: Remove absolute file paths (C:\Users\..., /usr/bin/...)
        clean = re.sub(r'([a-z]:\\[^\s]+)|(\/[^\s]+)', '', clean)
        
        return clean.strip()
        
    @classmethod
    def clean(cls, app_name, window_title):
        """Returns a sanitized tuple of (app_name, window_title)"""
        return cls.clean_process_name(app_name), cls.clean_window_title(window_title)
