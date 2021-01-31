from flask import url_for
from jinja2.utils import urlize
from flask_login import current_user

from flmapp.utils.template_filters import replace_newline

def make_deal_message_format(dest_user, messages):
    message_tag = ''
    for message in messages:
        message_tag += f'''
            <div class="msg-box dest-box">
                    <div class="msger-wrap">
                        <p>{ dest_user.username }</p>
                        <img class="u-icon" src={url_for("static", filename="user_image/" + dest_user.picture_path)}>
                    </div>
                <div class="speech-bubble-dest">
        '''
        for splitted_message in replace_newline(message.message):
            message_tag += f'<p>{ urlize(splitted_message) }</p>'
        message_tag += '''
                </div>'''
        message_tag += f'<p>{ message.create_at.strftime("%Y/%m/%d %H:%M") }</p>'
        message_tag += '''
            </div>
        '''
    return message_tag


def make_old_deal_message_format(dest_user, messages):
    message_tag = ''
    for message in messages[::-1]:
        if message.from_user_id == int(current_user.User_id):
            message_tag += f'''<div class="msg-box self-box"><div id="self-message-tag-{ message.DealMessage_id }">'''
            if message.is_checked:
                message_tag += '<p>既読<p>'
            message_tag += f'<p>{ message.create_at.strftime("%Y/%m/%d %H:%M") }</p>'
            message_tag += '''</div><div class="speech-bubble-self">'''
            for splitted_message in replace_newline(message.message):
                message_tag += f'<p>{ urlize(splitted_message) }</p>'
            message_tag += '''</div><div class="msger-wrap">'''
            message_tag += f'<img class="u-icon" src={ url_for("static", filename="user_image/" + current_user.picture_path) }>'
            message_tag += f'<p>{ current_user.username }</p>'
            message_tag += '''
                    </div>
                </div>
            '''
        else:
            message_tag += f'''
                <div class="msg-box dest-box">
                        <div class="msger-wrap">
                            <p>{ dest_user.username }</p>
                            <img class="u-icon" src={url_for("static", filename="user_image/" + dest_user.picture_path)}>
                        </div>
                    <div class="speech-bubble-dest">
            '''
            for splitted_message in replace_newline(message.message):
                message_tag += f'<p>{ urlize(splitted_message) }</p>'
            message_tag += '''
                    </div>'''
            message_tag += f'<p>{ message.create_at.strftime("%Y/%m/%d %H:%M") }</p>'
            message_tag += '''
                </div>
            '''
    return message_tag