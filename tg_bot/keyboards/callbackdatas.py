from aiogram.utils.callback_data import CallbackData

team_callback = CallbackData('teams','name')



confirmation_callback = CallbackData('confirmation', 'result', 'bd_data')

team_choice_callback = CallbackData('teams', 'team_id')
my_team_callback = CallbackData('type', 'topic' ,'team_id')

admin_callback_data = CallbackData('start','action')