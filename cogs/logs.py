const { EmbedBuilder } = require('discord.js');

// الدالة المسؤولة عن بناء الرسالة
function sendLog(channel, type, data) {
    const timestamp = Math.floor(Date.now() / 1000);
    const embed = new EmbedBuilder();

    // إعداد الألوان والأيقونات بناءً على النوع
    let color, title, description;

    if (type === 'join') {
        color = 0x00FF00; // أخضر
        description = `🟢 **MEMBER JOINED**\n\n👤 **Member**\n<@${data.memberId}>\n\n🕒 **Time**\n<t:${timestamp}:f>`;
    } 
    else if (type === 'leave') {
        color = 0xFF0000; // أحمر
        description = `🔴 **MEMBER LEFT**\n\n👤 **Member**\n${data.memberName}\n\n🕒 **Time**\n<t:${timestamp}:f>`;
    } 
    else if (type === 'role_action') {
        color = 0xFFD700; // أصفر
        description = `🟡 **ROLE UPDATED/DELETED**\n\n🛡️ **Role**\n${data.roleName}\n\n👮 **Moderator**\n<@${data.executorId || 'Unknown'}>\n\n🕒 **Time**\n<t:${timestamp}:f>`;
    }

    // تجميع الرسالة النهائية
    embed.setColor(color)
         .setDescription(`${description}\n\n━━━━━━━━━━━━━━━━━━\n**VOID Security Logs**`);

    // إرسال الرسالة
    channel.send({ embeds: [embed] }).catch(console.error);
}
