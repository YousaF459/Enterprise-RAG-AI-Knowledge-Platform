from conversations.models import Message


def history_conversation(conversation):

    history_results=Message.objects.filter(conversation=conversation)

    
    conversation_history_list=[]

    for item in history_results:
        conversation_history_list.append(
            {
                "ROLE":item.role,
                "TEXT":item.text
            }
        )
        

    return conversation_history_list
