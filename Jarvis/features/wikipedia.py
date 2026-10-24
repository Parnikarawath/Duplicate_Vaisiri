import wikipedia
 
 
def tell_me_about(topic):
    try:
        res = wikipedia.summary(topic, sentences=3)
        return res
    except Exception as e:
        print(e)
        return False

