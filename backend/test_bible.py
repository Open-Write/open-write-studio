import asyncio
from app.pipeline.orchestrator import system_prompt_for, _with_instructions, _exec_bible
from app.pipeline import profile_context
from app.routers.pipeline import _resolve_call_model, _make_model_call
from app.settings_store import get_writer_model

project = r'C:\Users\Nick\Documents\Open-Write\the-water-carrier'
wm = get_writer_model()
a_key, a_model, a_base = _resolve_call_model(wm)
call = _make_model_call(a_key, a_model, a_base)

system = system_prompt_for('bible')
characters = profile_context.character_context(project, 'architect')
world = profile_context.world_context(project)
state_obj = type('S', (), {'instructions': 'Short story about a misunderstood water carrier.'})()
user = _with_instructions(
    'Produce the bible for a new novel. Output three files delimited by markers.\n\n'
    + (characters + '\n\n' if characters else '')
    + (world + '\n\n' if world else ''),
    state_obj,
)

total = len(system) + len(user)
print(f'Model: {a_model}')
print(f'System: {len(system)} chars')
print(f'User: {len(user)} chars')
print(f'Total: {total} chars')

async def test():
    try:
        reply = await call(system, user)
        print(f'SUCCESS: {len(reply)} chars')
        print(reply[:500])
    except Exception as e:
        print(f'ERROR: {type(e).__name__}: {e}')

asyncio.run(test())
