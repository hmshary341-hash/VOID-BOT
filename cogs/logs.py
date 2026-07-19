const { EmbedBuilder } = require('discord.js');

/**
 * دالة إرسال السجلات (Logs)
 * @param {object} channel - قناة الـ logs
 * @param {string} type - نوع الحدث ('join', 'leave', 'role')
 * @param {object} data - البيانات المطلوبة (userId, roleName, executorId, avatarURL)
 */
function sendLog(channel, type, data) {
    const timestamp = Math.floor(Date.now() / 1000);
    const embed = new EmbedBuilder();

    let color, header;

    // تحديد الألوان والعناوين بناءً على النوع
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

    // بناء النص كما طلبته بالضبط
    let description = `${header}\n\n`;

    if (data.userId) description += `👤 **Member**\n<@${data.userId}>\n\n`;
    else description += `👤 **Member**\n${data.username}\n\n`;

    if (data.roleName) description += `🛡️ **Role**\n${data.roleName}\n\n`;
    
    if (data.executorId) description += `👮 **Moderator**\n<@${data.executorId}>\n\n`;

    description += `🕒 **Time**\n<t:${timestamp}:f>\n\n━━━━━━━━━━━━━━━━━━\n**VOID Security Logs**`;

    // تجميع الإمبيد
    embed.setColor(color)
         .setDescription(description);

    if (data.avatarURL) {
        embed.setThumbnail(data.avatarURL);
    }

    channel.send({ embeds: [embed] }).catch(console.error);
}

// --- كيفية استخدام الدالة في الأحداث (Events) ---

// 1. عند دخول عضو
client.on('guildMemberAdd', member => {
    const logChannel = member.guild.channels.cache.get('YOUR_LOG_CHANNEL_ID');
    sendLog(logChannel, 'join', { 
        userId: member.id, 
        avatarURL: member.user.displayAvatarURL({ dynamic: true }) 
    });
});

// 2. عند خروج عضو
client.on('guildMemberRemove', member => {
    const logChannel = member.guild.channels.cache.get('YOUR_LOG_CHANNEL_ID');
    sendLog(logChannel, 'leave', { 
        username: member.user.tag, 
        avatarURL: member.user.displayAvatarURL({ dynamic: true }) 
    });
});

// 3. عند حذف رتبة (مثال)
client.on('roleDelete', role => {
    const logChannel = role.guild.channels.cache.get('YOUR_LOG_CHANNEL_ID');
    // ملاحظة: هنا يجب جلب الـ executor من audit logs لاحقاً
    sendLog(logChannel, 'role', { 
        roleName: role.name, 
        executorId: 'ID_OF_MODERATOR' 
    });
});
