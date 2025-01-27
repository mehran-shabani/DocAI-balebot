from django.db import models
from django.utils.timezone import now


class BaleUser(models.Model):
    chat_id = models.CharField(max_length=50, unique=True)
    phone_number = models.CharField(max_length=15, unique=True)
    otp = models.CharField(max_length=6, blank=True, null=True)
    is_authenticated = models.BooleanField(default=False)

    # Custom fields
    daily_message_limit = models.PositiveIntegerField(default=23, verbose_name="Daily Message Limit")
    current_message_count = models.PositiveIntegerField(default=0, verbose_name="Current Message Count")
    token_limit = models.PositiveIntegerField(
        default=300,  # Default changed to 300
        verbose_name="Token Output Limit",
        help_text="Maximum tokens for the response. Must be between 300 and 1000."
    )

    ASSISTANT_ROLES = [
        ('general_physician', 'پزشک عمومی'),
        ('surgeon', 'جراح'),
        ('psychologist', 'روانشناس'),
        ('psychiatrist', 'روانپزشک'),
        ('pain_specialist', 'متخصص درد'),
        ('cardiologist', 'متخصص قلب'),
        ('neurologist', 'متخصص مغز و اعصاب'),
        ('endocrinologist', 'متخصص غدد'),
        ('pediatrician', 'متخصص اطفال'),
        ('dermatologist', 'متخصص پوست'),
        ('orthopedic', 'متخصص ارتوپدی'),
    ]
    assistant_role = models.CharField(
        max_length=50,
        choices=ASSISTANT_ROLES,
        default='general_physician',
        verbose_name="Assistant Role"
    )

    SYSTEM_ROLES = [
        ('therapeutic', 'سیستم درمانی'),
        ('diagnostic', 'سیستم تشخیصی'),
        ('triage', 'سیستم تریاژ'),
        ('predictive', 'سیستم پیش‌بینی'),
        ('educational', 'سیستم آموزشی'),
        ('research', 'سیستم پژوهشی'),
    ]
    system_role = models.CharField(
        max_length=50,
        choices=SYSTEM_ROLES,
        default='therapeutic',
        verbose_name="System Role"
    )

    ROLE_DESCRIPTIONS = {
        'general_physician': "شما یک پزشک عمومی بسیار با تجربه، متعهد به درمان بیماران، و بسیار با حوصله و با اخلاق هستید.",
        'surgeon': "شما یک جراح متخصص با مهارت بسیار بالا در انجام جراحی‌های پیچیده و حساس هستید.",
        'psychologist': "شما یک روانشناس با تجربه، مهربان و دلسوز برای کمک به سلامت روان افراد هستید.",
        'psychiatrist': "شما یک روانپزشک حرفه‌ای با توانایی تجویز دارو و ارائه مشاوره‌های روانپزشکی هستید.",
        'pain_specialist': "شما یک متخصص درد با تجربه در شناسایی و درمان انواع دردهای حاد و مزمن هستید.",
        'cardiologist': "شما یک متخصص قلب با دانش بالا در تشخیص و درمان بیماری‌های قلبی و عروقی هستید.",
        'neurologist': "شما یک متخصص مغز و اعصاب با توانایی در مدیریت بیماری‌های سیستم عصبی هستید.",
        'endocrinologist': "شما یک متخصص غدد با مهارت در شناسایی و درمان مشکلات هورمونی هستید.",
        'pediatrician': "شما یک متخصص اطفال مهربان و دلسوز با تجربه در درمان بیماری‌های کودکان هستید.",
        'dermatologist': "شما یک متخصص پوست حرفه‌ای با توانایی در درمان بیماری‌ها و مشکلات پوستی هستید.",
        'orthopedic': "شما یک متخصص ارتوپدی ماهر در تشخیص و درمان مشکلات استخوان و مفاصل هستید.",
    }

    def get_assistant_description(self):
        """Return the description for the assistant role."""
        return self.ROLE_DESCRIPTIONS.get(self.assistant_role, "توضیحی موجود نیست.")

    def reset_daily_count(self):
        """Reset daily message count for the user."""
        self.current_message_count = 0
        self.save()

    def increment_message_count(self):
        """Increment the user's current message count."""
        if self.current_message_count < self.daily_message_limit:
            self.current_message_count += 1
            self.save()
            return True
        return False

    def __str__(self):
        return f"{self.phone_number} - Auth: {self.is_authenticated}"


class ChatSession(models.Model):
    user = models.ForeignKey(
        BaleUser,
        on_delete=models.CASCADE,
        related_name='chat_sessions',
        verbose_name="User"
    )
    is_active = models.BooleanField(default=False)
    user_message = models.TextField(verbose_name="User Message", help_text="Message sent by the user.")
    bot_response = models.TextField(verbose_name="Bot Response", help_text="Response sent by the bot.")
    assistant_role = models.CharField(
        max_length=50,
        verbose_name="Assistant Role",
        help_text="Role of the assistant during this session."
    )
    system_role = models.CharField(
        max_length=50,
        verbose_name="System Role",
        help_text="Role of the system during this session."
    )
    created_at = models.DateTimeField(default=now, verbose_name="Created At")

    def __str__(self):
        return f"Session {self.id} - User: {self.user.phone_number} - Assistant: {self.assistant_role} - System: {self.system_role}"

    class Meta:
        verbose_name = "Chat Session"
        verbose_name_plural = "Chat Sessions"
        ordering = ['-created_at']
