from flask import url_for
from jinja2.utils import urlize

from flmapp.utils.template_filters import replace_newline

def make_deal_message_format(dest_user, messages):
    message_tag = ''
    for message in messages:
        message_tag += f'''
            <div class="msg-box">
                    <div class="msger-wrap">
                        <img src={url_for("static", filename="user_image/" + dest_user.picture_path)}>
                        <p>{ dest_user.username }</p>
                    </div>
                <div class="speech-bubble-dest">
        '''
        for splitted_message in replace_newline(message.message):
            message_tag += f'<p>{ urlize(splitted_message) }</p>'
        message_tag += '''
                </div>
            </div>
        '''
    return message_tag