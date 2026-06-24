import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from core.config import get_settings

logger = logging.getLogger(__name__)


class EmailService:
    def __init__(self):
        self.settings = get_settings()

    def _is_configured(self) -> bool:
        return bool(self.settings.smtp_user and self.settings.smtp_password)

    def send_reminder(
        self,
        to_email: str,
        member_name: str,
        drug_name: str,
        dosage: str,
        notes: str,
        reminder_time: datetime = None
    ) -> bool:
        if not self._is_configured():
            logger.warning("邮件服务未配置，跳过发送")
            return False

        if not to_email:
            logger.warning("收件人邮箱为空，跳过发送")
            return False

        if reminder_time is None:
            reminder_time = datetime.now()

        time_str = reminder_time.strftime("%Y年%m月%d日 %H:%M")

        subject = f"用药提醒 - {member_name} 该服药了"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: 'Microsoft YaHei', Arial, sans-serif; background-color: #f5f5f5; margin: 0; padding: 20px; }}
                .container {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 24px; text-align: center; }}
                .header h1 {{ margin: 0; font-size: 24px; }}
                .header p {{ margin: 8px 0 0; opacity: 0.9; font-size: 14px; }}
                .content {{ padding: 24px; }}
                .reminder-card {{ background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); border-radius: 12px; padding: 20px; color: white; margin-bottom: 20px; }}
                .reminder-card h2 {{ margin: 0 0 12px; font-size: 20px; }}
                .reminder-card .drug-name {{ font-size: 28px; font-weight: bold; margin: 12px 0; }}
                .info-row {{ display: flex; padding: 12px 0; border-bottom: 1px solid #eee; }}
                .info-row:last-child {{ border-bottom: none; }}
                .info-label {{ color: #666; width: 80px; }}
                .info-value {{ color: #333; font-weight: 500; flex: 1; }}
                .tips {{ background: #fff3cd; border-radius: 8px; padding: 16px; margin-top: 20px; }}
                .tips h3 {{ margin: 0 0 8px; color: #856404; font-size: 14px; }}
                .tips p {{ margin: 0; color: #856404; font-size: 13px; }}
                .footer {{ text-align: center; padding: 16px; color: #999; font-size: 12px; background: #fafafa; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>💊 用药提醒</h1>
                    <p>{time_str}</p>
                </div>
                <div class="content">
                    <p>亲爱的 <strong>{member_name}</strong>，您有一个用药提醒：</p>
                    
                    <div class="reminder-card">
                        <h2>该服药了</h2>
                        <div class="drug-name">💊 {drug_name}</div>
                        {f'<p>📝 {notes}</p>' if notes else ''}
                    </div>
                    
                    <div class="info-row">
                        <span class="info-label">服药人</span>
                        <span class="info-value">{member_name}</span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">提醒时间</span>
                        <span class="info-value">{time_str}</span>
                    </div>
                    {f'''
                    <div class="info-row">
                        <span class="info-label">备注</span>
                        <span class="info-value">{notes}</span>
                    </div>
                    ''' if notes else ''}
                    
                    <div class="tips">
                        <h3>💡 温馨提示</h3>
                        <p>请按时服药，如有疑问请咨询医生或药师。</p>
                    </div>
                </div>
                <div class="footer">
                    此邮件由家庭药箱管理系统自动发送
                </div>
            </div>
        </body>
        </html>
        """

        plain_content = f"""
{member_name}，您好！

您有一个用药提醒：

药品：{drug_name}
时间：{time_str}
{f"备注：{notes}" if notes else ""}

请按时服药，如有疑问请咨询医生或药师。

---
此邮件由家庭药箱管理系统自动发送
        """

        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = self.settings.default_from_email or self.settings.smtp_user
            msg["To"] = to_email

            msg.attach(MIMEText(plain_content, "plain", "utf-8"))
            msg.attach(MIMEText(html_content, "html", "utf-8"))

            with smtplib.SMTP_SSL(self.settings.smtp_host, self.settings.smtp_port) as server:
                server.login(self.settings.smtp_user, self.settings.smtp_password)
                server.sendmail(
                    self.settings.default_from_email or self.settings.smtp_user,
                    to_email,
                    msg.as_string()
                )

            logger.info(f"邮件发送成功: {to_email} - {drug_name}")
            return True

        except Exception as e:
            logger.error(f"邮件发送失败: {e}")
            return False


email_service = EmailService()
