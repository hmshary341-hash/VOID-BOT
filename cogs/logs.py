const { Client, GatewayIntentBits, Events, EmbedBuilder } = require('discord.js');

// إعدادات البوت مع الـ Intents الضرورية
const client = new Client({
    intents: [
        GatewayIntentBits.Guilds,
        GatewayIntentBits.GuildMessages,
        GatewayIntentBits.MessageContent
    ]
});

// أيدي قناة اللوج
const LOG_CHANNEL_ID = '1526625037808046241';

// دالة التحقق من قنوات التكت
function isTicketChannel(channel) {
    return channel.name && channel.name.toLowerCase().includes('ticket');
}

// 1. تسجيل الرسائل المحذوفة
client.on(Events.MessageDelete, async (message) => {
    if (!message.guild || message.author?.bot || isTicketChannel(message.channel)) return;

    const logChannel = message.guild.channels.cache.get(LOG_CHANNEL_ID);
    if (!logChannel) return;

    const embed = new EmbedBuilder()
        .setTitle('🗑️ رسالة محذوفة')
        .setColor('Red')
        .setAuthor({ name: message.author.tag, iconURL: message.author.displayAvatarURL() })
        .addFields({ name: 'المحتوى:', value: message.content || '*(رسالة فارغة أو وسائط)*' })
        .setTimestamp();

    logChannel.send({ embeds: [embed] }).catch(console.error);
});

// 2. تسجيل الرسائل المعدلة
client.on(Events.MessageUpdate, async (oldMessage, newMessage) => {
    if (!newMessage.guild || newMessage.author?.bot || oldMessage.content === newMessage.content || isTicketChannel(newMessage.channel)) return;

    const logChannel = newMessage.guild.channels.cache.get(LOG_CHANNEL_ID);
    if (!logChannel) return;

    const embed = new EmbedBuilder()
        .setTitle('✏️ رسالة معدلة')
        .setColor('Yellow')
        .setAuthor({ name: newMessage.author.tag, iconURL: newMessage.author.displayAvatarURL() })
        .addFields(
            { name: 'قبل التعديل:', value: oldMessage.content || '*(رسالة فارغة)*' },
            { name: 'بعد التعديل:', value: newMessage.content || '*(رسالة فارغة)*' }
        )
        .setTimestamp();

    logChannel.send({ embeds: [embed] }).catch(console.error);
});

// تشغيل البوت باستخدام المتغير الموجود في Railway
client.login(process.env.DISCORD_TOKEN);
