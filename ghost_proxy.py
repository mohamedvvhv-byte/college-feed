# الملف: ghost_proxy.py (Zoala-Eternal-Ghost Script)
from telethon import TelegramClient, events
from decouple import config
import json
import asyncio
from github import Github, InputGitTreeElement
import os

# ==============================================================================
# 0. إعدادات Zoala-Eternal-Node (سيتم قراءة المفاتيح من خادم Render)
# ==============================================================================
API_ID = config('API_ID', cast=int)
API_HASH = config('API_HASH')
GITHUB_TOKEN = config('GITHUB_TOKEN')
# تم دمج اسم المستودع الخاص بك:
GITHUB_REPO_NAME = "mohamedvvhv/college-feed" 
TARGET_FILE = 'data/college_feed.json'

# يرجى تعديل هذه القائمة فقط بـ (IDs) أو أسماء المستخدمين (Username) للمجموعات.
# **ملاحظة هامة:** تم استبدال روابط الدعوة بالروابط مباشرة للتشغيل الأول،
# ولكن يُفضل استبدالها بالـ IDs (-100...) بعد الحصول عليها من تشغيل هذا الملف.
TARGET_GROUPS = [
    'https://t.me/+MeDjVT5uqVc1MTJk', # الرابط الأول
    'https://t.me/+F9pjf_-jiKIzOWQ0', # الرابط الثاني
    'https://t.me/+HkZ7MNlXqDs0OTc0', # الرابط الثالث
    # الرابط الرابع تم حذفه لأنه مكرر.
]

# ==============================================================================

# 1. تهيئة تيليجرام
client = TelegramClient('zoala_college_session', API_ID, API_HASH)
client.parse_mode = 'html'

# 2. تهيئة GitHub
g = Github(GITHUB_TOKEN)
repo = g.get_repo(GITHUB_REPO_NAME)

# 3. دالة تحديث الملف على GitHub
def update_github_file(new_data):
    try:
        # قراءة محتوى الملف الحالي
        contents = repo.get_contents(TARGET_FILE)
        
        # تحويل البيانات إلى JSON مع ترميز UTF-8
        data_json = json.dumps(new_data, ensure_ascii=False, indent=4)
        
        # إنشاء شجرة git جديدة
        element = InputGitTreeElement(TARGET_FILE, '100644', data_json)
        
        # الحصول على آخر commit
        master_sha = repo.get_branch('main').commit.sha
        base_tree = repo.get_commit(master_sha).commit.tree
        
        # إنشاء شجرة جديدة
        tree = repo.create_git_tree([element], base_tree)
        
        # إنشاء commit جديدة
        commit = repo.create_git_commit(f"Zoala Update: {len(new_data)} messages", tree, [repo.get_git_commit(master_sha)])
        
        # تحديث الفرع الرئيسي
        repo.get_ref('heads/main').edit(commit.sha)
        
        print(f"[{client._current_session}] تم رفع التحديث بنجاح: {len(new_data)} رسالة.")
        
    except Exception as e:
        print(f"[{client._current_session}] خطأ في تحديث GitHub: {e}")

# 4. دالة جلب البيانات من GitHub (لتجنب مسح المحتوى القديم)
def fetch_existing_data():
    try:
        contents = repo.get_contents(TARGET_FILE)
        data = contents.decoded_content.decode('utf-8')
        return json.loads(data)
    except Exception as e:
        print(f"[{client._current_session}] فشل جلب البيانات الحالية من GitHub: {e}. سيبدأ بملف فارغ.")
        return []

# 5. معالج الرسائل الجديدة (الشبح)
@client.on(events.NewMessage(chats=TARGET_GROUPS))
async def handler_new_message(event):
    # تجاهل الرسائل الخدمية أو الإشعارات
    if not event.message.message and not event.message.media:
        return
    
    # الحصول على اسم المجموعة
    chat = await event.get_chat()
    group_name = chat.title if hasattr(chat, 'title') else str(chat.id)

    # تجهيز بيانات الرسالة
    post_data = {
        "timestamp": event.date.isoformat(),
        "group": group_name,
        "text": event.message.message,
        "media": None
    }
    
    # التعامل مع المرفقات (صور، ملفات، فيديوهات)
    if event.message.media:
        media_type = 'unknown'
        file_name = None

        if hasattr(event.message.media, 'document') and event.message.media.document:
            media_type = 'document'
            file_name = getattr(event.message.media.document, 'attributes', [None])[0].file_name if event.message.media.document.attributes else 'ملف'
        elif hasattr(event.message.media, 'photo'):
            media_type = 'photo'
        elif hasattr(event.message.media, 'webpage'):
            media_type = 'link_preview'

        post_data['media'] = {
            "type": media_type,
            "file_name": file_name
            # لا يتم رفع الملفات نفسها لتوفير الحوسبة المجانية
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
    
    # محاولة الاتصال والبدء (لأول مرة سيطلب رقم الهاتف والرمز)
    await client.start()
    
    # طباعة معرّفات المجموعات للمستخدم لتسهيل التعديل
    print("\n[معرفات المجموعات المستهدفة:")
    for group_entity in TARGET_GROUPS:
        try:
            # هنا سيحاول البوت الانضمام للمجموعات وطباعة الـ ID
            entity = await client.get_entity(group_entity)
            print(f"- الاسم: {entity.title if hasattr(entity, 'title') else 'Unknown'} | ID: {entity.id}")
        except Exception as e:
            print(f"- المعرّف: {group_entity} | فشل (قد لا يكون الرابط صحيحاً أو لا يوجد وصول). الخطأ: {e}")
    print("]\n")

    print("Zoala-Eternal-Ghost جاهز للاستقبال. الآن سنقوم بالاتصال بالخادم السحابي...")
    await client.run_until_disconnected()


if __name__ == '__main__':
    try:
        # سيتم تشغيل البوت مباشرة
        client.loop.run_until_complete(main())
    except Exception as e:
        print(f"خطأ رئيسي في Zoala-Ghost: {e}")