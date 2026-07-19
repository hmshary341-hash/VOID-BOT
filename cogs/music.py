import discord
from discord.ext import commands
import wavelink
import os

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        # ربط البوت بـ Lavalink باستخدام المتغيرات التي ضبطناها في Railway
        node = wavelink.Node(
            uri=f"http://{os.getenv('LAVALINK_HOST')}:{os.getenv('LAVALINK_PORT')}",
            password=os.getenv('LAVALINK_PASSWORD')
        )
        await wavelink.Pool.connect(nodes=[node], client=self.bot)
        print("✅ تم الاتصال بـ Lavalink بنجاح!")

    @commands.command()
    async def play(self, ctx, *, search: str):
        """أمر تشغيل الأغنية"""
        if not ctx.author.voice:
            return await ctx.send("❌ | لازم تدخل قناة صوتية أولاً!")
        
        vc = ctx.voice_client
        if not vc:
            vc = await ctx.author.voice.channel.connect(cls=wavelink.Player)

        # البحث عن الأغنية
        tracks = await wavelink.Playable.search(search)
        if not tracks:
            return await ctx.send("🔍 | للأسف ما لقيت شي بهذا الاسم.")
        
        track = tracks[0]
        await vc.play(track)
        await ctx.send(f"🎵 | جاري تشغيل: **{track.title}**")

    @commands.command()
    async def stop(self, ctx):
        """أمر إيقاف الموسيقى"""
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
            await ctx.send("⏹️ | تم إيقاف الموسيقى والخروج من القناة.")

async def setup(bot):
    await bot.add_cog(Music(bot))
