const { EmbedBuilder } = require('discord.js');

// قم بوضع الأيدي هنا لسهولة التعديل مستقبلاً
const LOG_CHANNEL_ID = '1526625037808046241';

// دالة إرسال السجلات (Logs)
function sendLog(channel, type, data) {
    const timestamp = Math.floor(Date.now() / 1000);
    const embed = new EmbedBuilder();

    let color, header;

    if (type === 'join') {
        color = 0x00FF00; // أخضر
        header = '🟢 MEMBER JOINED';
    } else if (type === 'leave') {
        color = 0xFF0000; // أحمر
        header = '🔴 MEMBER LEFT';
    } else if (type === 'role') {
        color = 0xFFD700; // أصفر
        header = '🟡 ROLE UPDATED/DELETED';
    }

    let description = `${header}\n\n`;
    if (data.userId) description += `👤 **Member**\n<@${data.userId}>\n\n`;
    else description += `👤 **Member**\n${data.username}\n\n`;
    if (data.roleName) description += `🛡️ **Role**\n${data.roleName}\n\n`;
    if (data.executorId) description += `👮 **Moderator**\n<@${data.executorId}>\n\n`;

    description += `🕒 **Time**\n<t:${timestamp}:f>\n\n━━━━━━━━━━━━━━━━━━\n**VOID Security Logs**`;

    embed.setColor(color).setDescription(description);
    if (data.avatarURL) embed.setThumbnail(data.avatarURL);

    channel.send({ embeds: [embed] }).catch(err => console.error("خطأ في إرسال الـ Log:", err));
}

// --- الأحداث (Events) ---

// 1. دخول عضو
client.on('guildMemberAdd', member => {
    const logChannel = member.guild.channels.cache.get(LOG_CHANNEL_ID);
    if (!logChannel) return;
    sendLog(logChannel, 'join', { 
        userId: member.id, 
        avatarURL: member.user.displayAvatarURL({ dynamic: true }) 
    });
});

// 2. خروج عضو
client.on('guildMemberRemove', member => {
    const logChannel = member.guild.channels.cache.get(LOG_CHANNEL_ID);
    if (!logChannel) return;
    sendLog(logChannel, 'leave', { 
        username: member.user.tag, 
        avatarURL: member.user.displayAvatarURL({ dynamic: true }) 
    });
});
