import asyncio
import os
import platform
import aiohttp
import aiofiles
from rich import print
from rich.prompt import Prompt
from queue import Queue

if platform.system() == "Windows" and asyncio.get_event_loop_policy().get_event_loop() is asyncio.ProactorEventLoop:
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
save_queue = asyncio.Queue()
global_counter = 0


def load_unique_tokens(*filenames):
    combined_tokens = []

    for filename in filenames:
        with open(filename, 'r') as file:
            combined_tokens.extend(file.read().splitlines())

    unique_tokens = [token for token in combined_tokens if combined_tokens.count(token) == 1]

    return unique_tokens



def clear_screen():
    if os.name == 'nt':
        os.system("cls")
    else:
        os.system("clear")


async def save_to_file():
    async with aiofiles.open("data/blacklist.txt", "a") as file:
        while not save_queue.empty():
            users_chunk = await save_queue.get()
            for user in users_chunk:
                username = user.lstrip('@') 
                await file.write(username + "\n")
                
async def write_token_to_file(token, type):
    async with aiofiles.open(f'data/{type}_tokens.txt', 'a') as file:
        await file.write(f"{token}\n")
    
clear_screen()
header_text = """
[bold gold1] _     _    _____                        
$$\   $$\  $$$$$$\                       $$\               
$$ |  $$ |$$  __$$\                      $$ |              
\$$\ $$  |$$ /  $$ |$$\   $$\  $$$$$$\ $$$$$$\    $$$$$$\  
 \$$$$  / $$ |  $$ |$$ |  $$ |$$  __$$\\_$$  _|  $$  __$$\ 
 $$  $$<  $$ |  $$ |$$ |  $$ |$$ /  $$ | $$ |    $$$$$$$$ |
$$  /\$$\ $$ $$\$$ |$$ |  $$ |$$ |  $$ | $$ |$$\ $$   ____|
$$ /  $$ |\$$$$$$ / \$$$$$$  |\$$$$$$  | \$$$$  |\$$$$$$$\ 
\__|  \__| \___$$$\  \______/  \______/   \____/  \_______|
               \___| [green]v1 [white]> Telegram: [cyan]@fatbeebhw 
               [green]You like it? Tip it <3: [cyan]0x7C9EB6dF2349820D27D69805193d7806A7689ade                                                                                                                                           
"""
print(f'{header_text}')
tags_number = Prompt.ask("[bold blue_violet]👥 Tags per post[/bold blue_violet]",
                     default='15')

tokens_conc = Prompt.ask("[bold blue_violet]⚙️ Tokens at same time[/bold blue_violet]",
                     default='1')

max_qs = Prompt.ask("[bold blue_violet]🔥 Max Quotes[/bold blue_violet]",
                     default='350')

post_id = Prompt.ask("[bold blue_violet]🎯 Post ID[/bold blue_violet]",
                     default="1700259403411431907")
are_you_ready = Prompt.ask(
    "[bold green_yellow]🚀 Are you ready?[/bold green_yellow]", choices=["Yes", "No"], default="Yes")

if are_you_ready != "Yes":
    print("[bold red]🛑 Stopping...[/bold red]")
    exit()

clear_screen()

status_text = f"🎯 [bold green_yellow]Target:[white] {post_id}"
print(header_text)
print("[bold green_yellow]🚀 Let's go![/bold green_yellow]")
print(status_text)
def read_users_and_enqueue(file_path, blacklist_path="data/blacklist.txt", chunk_size=int(tags_number)):
    users_queue = Queue()
    total_users = 0
    chunk_count = 0

    blacklist = set()
    with open(blacklist_path, 'r') as bl_file:
        for line in bl_file:
            blacklist_user = line.strip()
            blacklist.add(blacklist_user)

    with open(file_path, 'r') as file:
        chunk = []
        for line in file:
            user = "@" + line.strip()
            if user not in blacklist:
                chunk.append(user)
                total_users += 1
                if len(chunk) == chunk_size:
                    users_queue.put(chunk)
                    chunk = []
                    chunk_count += 1
        if chunk:
            users_queue.put(chunk)
            chunk_count += 1

    return users_queue, total_users, chunk_count

tokens = load_unique_tokens('tokens.txt', 'data/used_tokens.txt', 'data/dead_tokens.txt')


if not tokens:
    print("\n[red][❗] There are no tokens. Exiting...\n")
    exit()
else:
    print(f"[bold light_goldenrod2][⚠️] Loaded {len(tokens)} tokens.")




async def engage(token, post_id, users_queue):
    global global_counter
    try:
        async with aiohttp.ClientSession() as client:
            headers = {
                'authority': 'twitter.com',
                'accept': '*/*',
                'accept-language': 'en-US,en;q=0.9',
                'authorization': 'Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA',
                'content-type': 'application/json',
                'dnt': '1',
                'origin': 'https://twitter.com',
                'referer': 'https://twitter.com/compose/tweet',
                'sec-ch-ua': '"Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-origin',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
                'x-twitter-active-user': 'yes',
                'x-twitter-auth-type': 'OAuth2Session',
                'x-twitter-client-language': 'en',
            }
            async with client.post('https://twitter.com/i/api/1.1/account/update_profile.json', cookies={'auth_token': token}, headers=headers, timeout=15) as resp:
                if 'ct0' in resp.cookies:
                    ct0 = resp.cookies['ct0'].value  
                else:
                    print(f"[red][❌] Failed to retrieve ct0 for token: [white]{token}")
                    return


                cookies = {
                    'auth_token': token,
                    'ct0': ct0
                }
                headers['x-csrf-token'] = ct0
                
            async with client.post('https://twitter.com/i/api/1.1/account/update_profile.json', headers=headers, cookies=cookies) as response:
                    if response.status != 200:
                        print(f"[red][❌] Token is dead: [white]{token}")
                        await write_token_to_file(token, "dead")
                        return

            counter = 0
            async def make_request():
                nonlocal counter
                global global_counter
                while not users_queue.empty():
                    users_chunk = users_queue.get()
                    tweet_text = ' '.join(users_chunk)
                    json_data = {
                        'variables': {
                            'tweet_text': tweet_text,
                            'attachment_url': f'https://twitter.com/x/status/{post_id}',
                            'dark_request': False,
                            'media': {
                                'media_entities': [],
                                'possibly_sensitive': False,
                            },
                            'semantic_annotation_ids': [],
                        },
                        'features': {
                            'c9s_tweet_anatomy_moderator_badge_enabled': True,
                            'tweetypie_unmention_optimization_enabled': True,
                            'responsive_web_edit_tweet_api_enabled': True,
                            'graphql_is_translatable_rweb_tweet_is_translatable_enabled': True,
                            'view_counts_everywhere_api_enabled': True,
                            'longform_notetweets_consumption_enabled': True,
                            'responsive_web_twitter_article_tweet_consumption_enabled': False,
                            'tweet_awards_web_tipping_enabled': False,
                            'responsive_web_home_pinned_timelines_enabled': True,
                            'longform_notetweets_rich_text_read_enabled': True,
                            'longform_notetweets_inline_media_enabled': True,
                            'responsive_web_graphql_exclude_directive_enabled': True,
                            'verified_phone_label_enabled': False,
                            'freedom_of_speech_not_reach_fetch_enabled': True,
                            'standardized_nudges_misinfo': True,
                            'tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled': True,
                            'responsive_web_media_download_video_enabled': False,
                            'responsive_web_graphql_skip_user_profile_image_extensions_enabled': False,
                            'responsive_web_graphql_timeline_navigation_enabled': True,
                            'responsive_web_enhance_cards_enabled': False,
                        },
                        'queryId': '5V_dkq1jfalfiFOEZ4g47A',
                    }
                    try:
                        response = await client.post('https://twitter.com/i/api/graphql/5V_dkq1jfalfiFOEZ4g47A/CreateTweet',
                                                    cookies=cookies, headers=headers, json=json_data, timeout=15)
                        if "in_reply_to_screen_name" in await response.text():
                            counter += 1
                            #print(f"[✅] ({token}) has quoted | Count: {counter}")
                            return True
                        else:
                            #print(f"[❌] Died or failed to Quote. ({token}) | Count: {counter}")
                            users_queue.put(users_chunk)
                            await save_queue.put(users_chunk)
                            return False
                    except Exception as e:
                        print(f"[❌] Unexpected error: {e}")
                        users_queue.put(users_chunk)
                        return False

            tasks = [make_request() for _ in range(int(max_qs))]  
            await asyncio.gather(*tasks)
            if counter > 1:
                global_counter += counter
                formatted_global_counter = "{:,}".format(global_counter)
                formatted_total = "{:,}".format(global_counter * int(tags_number))
                print(f"[✅] [green]([white]{token}[green]) [white]quoted [green]{counter}[white] times. | Quotes: [green]{formatted_global_counter} [white]Tags: [green]{formatted_total}")
                await write_token_to_file(token, "used")
                await save_to_file()
                return
            
    except aiohttp.ClientError as e:
        print(f"[red][❌] Request error encountered for token {token}: {e}")
        return
    except Exception as e:
        print(f"[red][❌] Unexpected error encountered for token {token}: {e}")
        return


async def run_all(tokens, post_id):
    users_queue, total_users, chunk_count = read_users_and_enqueue('users.txt')
    print(f"Total Sets: {chunk_count}, Total Users: {total_users}")
    semaphore = asyncio.Semaphore(int(tokens_conc))  

    async def main_worker(token):
        async with semaphore:
            await engage(token, post_id, users_queue)


    main_tasks = [main_worker(token) for token in tokens]

    await asyncio.gather(*main_tasks)

asyncio.run(run_all(tokens, post_id))