import discord
import os
import datetime

bot_owner_id = 445492984746737664
admin_id = [445492984746737664, 318195772736798720, 840742124286378045]
management_interface_channel_id = 1085074574296764466
vip_role_id = 1077038181255479337

def get_environ(key:str) -> dict:
    return {data[0]: data[1] for data in (item.split(":") for item in os.environ[key].split(","))}

intents=discord.Intents.all()
bot = discord.Bot(intents=intents)

def get_base_embed() -> discord.Embed:
    embed = discord.Embed(colour=0xC9C8FF, timestamp=datetime.datetime.now())
    embed.set_author(name="Luna", url="https://github.com/mrken-community/Luna-v3", icon_url=bot.user.avatar.url.replace("size=1024", "size=64"))
    embed.set_footer(text="Made with love ❤")
    return embed

class VIPAppModal(discord.ui.Modal):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.add_item(discord.ui.InputText(label="FXGT UID", required=True))
        self.add_item(discord.ui.InputText(label="Bitget UID", required=False))
        self.add_item(discord.ui.InputText(label="ByBit UID", required=False))
        self.add_item(discord.ui.InputText(label="OKX UID", required=False))

    async def callback(self, interaction: discord.Interaction):
        embed_for_user = get_base_embed()
        embed_for_user.title = "無料VIP申請フォーム - 申請を受け付けました。"
        embed_for_user.description = "１～２週間経過しても承認されない場合は確認の上、再申請をお願い致します。"
        await interaction.response.send_message(embed=embed_for_user, ephemeral=True)

        embed_for_admin = get_base_embed()
        embed_for_admin.title = "無料VIP申請フォーム - 受信した申請"
        embed_for_admin.add_field(name="LunaFunction", value=f"vip_form:{interaction.user.id}")
        embed_for_admin.add_field(name="申請者", value=f"{interaction.user.mention} (@{interaction.user.global_name})")
        embed_for_admin.add_field(name="FXGT", value=self.children[0].value, inline=False)
        embed_for_admin.add_field(name="Bitget", value=self.children[1].value, inline=False)
        embed_for_admin.add_field(name="ByBit", value=self.children[2].value, inline=False)
        embed_for_admin.add_field(name="OKX", value=self.children[3].value, inline=False)
        mici = bot.get_channel(management_interface_channel_id)
        sent_embed_for_admin = await mici.send(embed=embed_for_admin)
        await sent_embed_for_admin.add_reaction("✅")

class VIPAppButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="申請フォームへ", custom_id="vip-app-button", style=discord.ButtonStyle.primary, emoji="👑")
    async def button_callback(self, button, interaction):
        await interaction.response.send_modal(VIPAppModal(title="無料VIP申請フォーム"))

@bot.event
async def on_ready():
    bot.add_view(VIPAppButton())
    print("(Luna) Ready")

@bot.event
async def on_raw_reaction_add(payload):
    if payload.user_id == bot.user.id:
        return
    message = await bot.get_channel(payload.channel_id).fetch_message(payload.message_id)
    for embed in message.embeds:
        for field in embed.fields:
            if field.name == "LunaFunction":
                func_data = field.value.split(":")
                match func_data[0]:
                    case "vip_form":
                        applicated_user = await message.guild.fetch_member(func_data[1])
                        vip_role = discord.utils.get(message.guild.roles, id=vip_role_id)
                        await applicated_user.add_roles(vip_role)
                        await message.add_reaction("👑")
                        user = bot.get_user(payload.user_id)
                        await message.remove_reaction(payload.emoji, user)
                        base_embed = get_base_embed()
                        base_embed.title = "無料VIP申請フォーム - 受理完了"
                        base_embed.add_field(name="現在のvipの人数", value=f"{len(vip_role.members)}人")
                        await message.reply(embed=base_embed)

@bot.slash_command(description="管理用コマンド")
async def execute(ctx, command : str, args : str = None):
    try:
        if ctx.author.id in admin_id:
            match command:
                case "summon":
                    match args:
                        case "vip_form":
                            base_embed = get_base_embed()
                            base_embed.title = "無料VIP申請フォーム"
                            base_embed.description = "FXGTのUID + (BitGet, ByBit, OKX)の3つの中から1つ以上のUIDを入力してください。"
                            await ctx.respond(embed=base_embed, view=VIPAppButton())
                            return
                case "analytics":
                    invite_uses = 0
                    invites = await ctx.guild.invites()
                    for invite in invites:
                        invite_uses += invite.uses
                    base_embed = get_base_embed()
                    base_embed.title = "アナリティクス"
                    base_embed.add_field(name="サーバー名", value=ctx.guild.name)
                    base_embed.add_field(name="ユーザー数",value=ctx.guild.member_count)
                    base_embed.add_field(name="有効な招待リンクの数",value=len(invites))
                    base_embed.add_field(name="有効な招待リンクの使用数",value=invite_uses)
                    await ctx.respond(embed=base_embed, ephemeral=True)
                    return
    except Exception as e:
        print(f"Execute error: {e}")
    await ctx.delete()

bot.run(get_environ("Luna_v3")["token"])