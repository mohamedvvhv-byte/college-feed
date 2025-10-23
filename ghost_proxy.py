# الملف: ghost_proxy.py (Zoala-Eternal-Ghost Script - FINAL with Media Upload)
from telethon import TelegramClient, events
from decouple import config
import json
import asyncio
from github import Github, InputGitTreeElement, Auth
import os
import io # مكتبة للتعامل مع البيانات الثنائية (الصور)
import base64 # للترميز المطلوب لـ GitHub API

# ==============================================================================
# 0. إعدادات Zoala-Eternal-Node (سيتم قراءة المفاتيح من خادم Render)
# ==============================================================================
# ملاحظة: تم إدراج القيم مباشرة هنا لتجاوز مشاكل جهازك، لكن Render سيستخدم مفاتيح البيئة.
API_ID = 21657323
API_HASH = "42a5e8f1171b74d44dbda8f07514942c"
GITHUB_TOKEN = "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"

# اسم المستودع (مُعدَّل):
GITHUB_REPO_NAME = "mohamedvvhv/college-feed" 
TARGET_FILE = 'data/college_feed.json'
MEDIA_FOLDER = 'data/media/' # المجلد الجديد لتخزين الصور

# تم استبدال الروابط بالـ IDs الدائمة التي حصلنا عليها:
TARGET_GROUPS = [
    -10013197584691, # Grammatik und Texte und Wortschatzerwerb
    -10012963059292, # الفرقة الأولى مادة اللغة العربية قسم اللغة الألمانية
    -10012910026944, # الفرقة الأولى قسم اللغة الالمانية د/روضه
]

# ==============================================================================

# 1. تهيئة تيليجرام
client = TelegramClient('zoala_college_session', API_ID, API_HASH)
client.parse_mode = 'html'

# 2. تهيئة GitHub (إعادة التفعيل)
try:
    auth = Auth.Token(GITHUB_TOKEN)
    g = Github(auth=auth)
    repo = g.get_repo(GITHUB_REPO_NAME)
    GITHUB_ENABLED = True
except Exception as e:
    print(f"تحذير: فشل تهيئة GitHub (قد يكون التوكن غير صالح): {e}")
    GITHUB_ENABLED = False

# 3. دالة تحديث الملف على GitHub
# (لم يتغير)

# 4. دالة جلب البيانات من GitHub
# (لم يتغير)

# 5. دالة لرفع الوسائط إلى GitHub (وظيفة جديدة)
async def upload_media_to_github(message, file_extension):
    if not GITHUB_ENABLED:
        return None
    try:
        # تنزيل الملف بشكل متزامن
        file_buffer = await client.download_media(message, bytes)
        
        # إنشاء اسم ملف فريد (باستخدام معرف الرسالة والوقت)
        file_name = f"{message.id}_{message.date.timestamp():.0f}{file_extension}"
        github_path = MEDIA_FOLDER + file_name
        
        # الترميز Base64 لمتطلبات GitHub API
        content_base64 = base64.b64encode(file_buffer).decode('utf-8')
        
        # استخدام create_file لرفع الملف مباشرة (أسهل للصور الصغيرة)
        repo.create_file(
            path=github_path,
            message=f"Zoala Media: Upload {file_name}",
            content=content_base64,
        )

        # رابط الوصول العام للصورة (RAW URL)
        raw_url = f"https://raw.githubusercontent.com/{GITHUB_REPO_NAME}/main/{github_path}"
        print(f"[{client._current_session}] تم رفع الصورة بنجاح: {raw_url}")
        return raw_url

    except Exception as e:
        print(f"[{client._current_session}] خطأ في رفع الوسائط إلى GitHub: {e}")
        return None

# 6. معالج الرسائل الجديدة (الشبح)
@client.on(events.NewMessage(chats=TARGET_GROUPS))
async def handler_new_message(event):
    # تجاهل الرسائل الخدمية أو الإشعارات
    if not event.message.message and not event.message.media:
        return
    
    # الحصول على اسم المجموعة
    chat = await event.get_chat()
    group_name = chat.title if hasattr(chat, 'title') else str(chat.id)
    
    media_url = None
    
    # التعامل مع المرفقات (صور، ملفات، فيديوهات)
    if event.message.media:
        media_type = 'unknown'
        file_name = None
        file_ext = ''

        if hasattr(event.message.media, 'photo'):
            media_type = 'photo'
            file_ext = '.jpg' # افتراضياً للصور
            media_url = await upload_media_to_github(event.message, file_ext) # **تحميل الصورة**
        
        elif hasattr(event.message.media, 'document') and event.message.media.document:
            media_type = 'document'
            doc = event.message.media.document
            file_name = getattr(doc, 'attributes', [None])[0].file_name if doc.attributes else 'ملف'
            # نحصل على الامتداد الحقيقي للملف
            if file_name and '.' in file_name:
                file_ext = '.' + file_name.split('.')[-1].lower()
            
            # إذا كان ملفاً صغيراً (مثل GIFs أو ملفات نصية صغيرة)، يمكننا رفعه أيضاً.
            if file_ext in ['.gif', '.png', '.pdf', '.txt', '.jpg', '.jpeg']:
                media_url = await upload_media_to_github(event.message, file_ext) # **تحميل الملف**

        elif hasattr(event.message.media, 'webpage'):
            media_type = 'link_preview'
            
    # تجهيز بيانات الرسالة
    post_data = {
        "timestamp": event.date.isoformat(),
        "group": group_name,
        "text": event.message.message,
        "media": None
    }
    
    if media_url:
        # إذا نجحنا في الرفع، نسجل رابط الوصول المباشر
        post_data['media'] = {
            "type": media_type,
            "url": media_url,
            "file_name": file_name
        }
    elif event.message.media:
         # إذا فشل الرفع (أو كان الملف كبيراً جداً/غير مدعوم)، نضع تنبيهاً
        post_data['media'] = {
            "type": media_type,
            "file_name": file_name,
            "url": "NOT_UPLOADED_TOO_LARGE_OR_UNSUPPORTED"
        }
    
    # جلب البيانات الحالية وإضافة الرسالة الجديدة
    existing_data = await asyncio.get_event_loop().run_in_executor(None, fetch_existing_data)
    
    # فحص التكرار (لتجنب الرسائل المكررة عند إعادة تشغيل البوت)
    is_duplicate = any(p['timestamp'] == post_data['timestamp'] and p['text'] == post_data['text'] for p in existing_data)
    
    if not is_duplicate:
        existing_data.insert(0, post_data) # إضافة الرسالة الجديدة في البداية (الأحدث أولاً)
        
        # حفظ آخر 500 رسالة فقط للحفاظ على سرعة الملف
        updated_data = existing_data[:500] 
        
        # تحديث GitHub (تنفيذ في خلفية منفصلة لتجنب إيقاف البوت)
        await asyncio.get_event_loop().run_in_executor(None, update_github_file, updated_data)
        
        print(f"[{client._current_session}] رسالة جديدة من {group_name}: {post_data['text'][:30]}...")
    else:
        print(f"[{client._current_session}] تم تجاهل رسالة مكررة من {group_name}.")

async def main():
    print("Zoala-Eternal-Ghost بدأ التشغيل...")
    await client.start()
    print("\n[معرّفات المجموعات المستهدفة تم تحميلها بنجاح.]")
    print("Zoala-Eternal-Ghost جاهز للاستقبال. يتم الآن الاتصال بخادم Render...")
    await client.run_until_disconnected()


if __name__ == '__main__':
    try:
        client.loop.run_until_complete(main())
    except Exception as e:
        print(f"خطأ رئيسي في Zoala-Ghost: {e}")