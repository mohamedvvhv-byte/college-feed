# الملف: ghost_proxy.py (Zoala-Eternal-Ghost Script)
from telethon import TelegramClient, events
from decouple import config
import json
import asyncio
# تم تعطيل المكتبات المتعلقة بـ GitHub مؤقتاً لتسهيل تسجيل الدخول
# from github import Github, InputGitTreeElement
import os

# ==============================================================================
# 0. إعدادات Zoala-Eternal-Node (مفاتيحك مُدمجة هنا مؤقتاً للتسجيل)
# ==============================================================================
API_ID = 21657323
API_HASH = "42a5e8f1171b74d44dbda8f07514942c"
GITHUB_TOKEN = "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" # سنستخدمه لاحقاً
# اسم المستودع (مُعدَّل):
GITHUB_REPO_NAME = "mohamedvvhv/college-feed" 
TARGET_FILE = 'data/college_feed.json'

# يرجى تعديل هذه القائمة لاحقاً بـ (IDs) بعد الحصول عليها.
TARGET_GROUPS = [
    'https://t.me/+MeDjVT5uqVc1MTJk',
    'https://t.me/+F9pjf_-jiKIzOWQ0',
    'https://t.me/+HkZ7MNlXqDs0OTc0',
]

# ==============================================================================

# 1. تهيئة تيليجرام
client = TelegramClient('zoala_college_session', API_ID, API_HASH)
client.parse_mode = 'html'

# 2. تهيئة GitHub (تم تعطيل هذا القسم مؤقتاً لتجنب خطأ 401)
# from github import Auth
# auth = Auth.Token(GITHUB_TOKEN)
# g = Github(auth=auth)
# repo = g.get_repo(GITHUB_REPO_NAME)

# 3. دالة تحديث الملف على GitHub (تم تعطيل هذه الدالة مؤقتاً)
def update_github_file(new_data):
    print("لا يمكن تحديث GitHub: تم تعطيل وظائف GitHub مؤقتاً لجمع الـ IDs.")
    # لا شيء يحدث فعلياً هنا

# 4. دالة جلب البيانات من GitHub (تم تعطيل هذه الدالة مؤقتاً)
def fetch_existing_data():
    return [] # سيبدأ بملف فارغ لأن وظيفة GitHub مُعطلة

# 5. معالج الرسائل الجديدة (الشبح)
@client.on(events.NewMessage(chats=TARGET_GROUPS))
async def handler_new_message(event):
    # تجاهل الرسائل الخدمية أو الإشعارات
    if not event.message.message and not event.message.media:
        return
    
    # الحصول على اسم المجموعة
    chat = await event.get_chat()
    group_name = chat.title if hasattr(chat, 'title') else str(chat.id)

    # تجهيز بيانات الرسالة (لن يتم رفعها، فقط للطباعة)
    post_data = {
        "timestamp": event.date.isoformat(),
        "group": group_name,
        "text": event.message.message,
        "media": None
    }
    
    print(f"[{client._current_session}] رسالة جديدة من {group_name}: {post_data['text'][:30]}...")

    # هذا الجزء معطل لأنه يعتمد على وظيفة تحديث GitHub
    # existing_data = await asyncio.get_event_loop().run_in_executor(None, fetch_existing_data)
    # updated_data = existing_data[:500] 
    # await asyncio.get_event_loop().run_in_executor(None, update_github_file, updated_data)


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

    print("Zoala-Eternal-Ghost جاهز للاستقبال. يرجى إرسال الـ IDs التي ظهرت لك وإيقاف البوت (Ctrl+C).")
    await client.run_until_disconnected()


if __name__ == '__main__':
    try:
        # سيتم تشغيل البوت مباشرة
        client.loop.run_until_complete(main())
    except Exception as e:
        print(f"خطأ رئيسي في Zoala-Ghost: {e}")