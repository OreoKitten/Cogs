import sqlite3
from datetime import datetime

import discord
from discord.ext import commands

class scorekeeping(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.conn = sqlite3.connect('scores.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS scores
                                (id INTEGER PRIMARY KEY AUTOINCREMENT,
                                winner_id INTEGER,
                                loser_id INTEGER,
                                game_mode TEXT,
                                date TEXT)''')
        self.conn.commit()

    def record_result(self, winner_id, loser_id, game_mode):
        now = datetime.now()
        date = now.strftime('%Y-%m-%d %H:%M:%S')
        self.cursor.execute('INSERT INTO scores (winner_id, loser_id, game_mode, date) VALUES (?, ?, ?, ?)',
                             (winner_id, loser_id, game_mode, date))
        self.conn.commit()

    @commands.command()
    async def record(self, ctx, opponent: discord.Member, game_mode: str, result: str):
        if result.lower() not in ('win', 'loss'):
            await ctx.send('Result must be either "win" or "loss".')
            return
        if game_mode not in ('team_deathmatch', 'domination', 'search_and_destroy'):
            await ctx.send('Invalid game mode.')
            return
        if ctx.author == opponent:
            await ctx.send('You cannot play against yourself.')
            return
        self.record_result(ctx.author.id, opponent.id, game_mode)
        if result.lower() == 'win':
            winner = ctx.author
            loser = opponent
        else:
            winner = opponent
            loser = ctx.author
        await ctx.send(f'{winner.mention} defeated {loser.mention} in {game_mode}.')

    @commands.command()
    async def recent_results(self, ctx):
        self.cursor.execute('SELECT winner_id, loser_id, game_mode, date FROM scores ORDER BY date DESC LIMIT 5')
        results = self.cursor.fetchall()
        output = []
        for winner_id, loser_id, game_mode, date in results:
            winner = self.bot.get_user(winner_id)
            loser = self.bot.get_user(loser_id)
            output.append(f'{winner.name} defeated {loser.name} in {game_mode} on {date}.')
        if output:
            await ctx.send('\n'.join(output))
        else:
            await ctx.send('No recent results.')

def setup(bot):
    bot.add_cog(scorekeeping(bot))

