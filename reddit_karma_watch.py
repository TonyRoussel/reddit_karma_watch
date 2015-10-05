import praw
import argparse
import sys
import time
import RPi.GPIO as GPIO

def get_arg_user():
    argparser = argparse.ArgumentParser()
    argparser.add_argument("username")
    args = argparser.parse_args()
    return args.username

def init_reddit(uagent, cachetime=1):
    return praw.Reddit(user_agent=uagent, cache_timeout=cachetime)

def init_gpio(gpio_list):
    GPIO.setmode(GPIO.BOARD)
    for gpio in gpio_list:
        GPIO.setup(gpio, GPIO.OUT)
    return

def gpio_blink(pin, bton=1., btoff=None):
    GPIO.output(pin, GPIO.HIGH)
    time.sleep(bton)
    GPIO.output(pin, GPIO.LOW)
    if btoff is not None:
        time.sleep(btoff)
    return

def link_blink(n, pin):
    for i in xrange(n):
        for x in xrange(3):
            gpio_blink(pin, 0.08, 0.08)
    return

def comment_blink(n, pin):
    for i in xrange(n):
        gpio_blink(pin, 1, 0.5)
    return

def signal_link_karma_shift(link_karma_diff, gpio_plus, gpio_minus):
    if link_karma_diff < 0:
        print "Link karma shift %d" % (link_karma_diff)
        link_blink(abs(link_karma_diff), gpio_minus)
    elif link_karma_diff > 0:
        print "Link karma shift %d" % (link_karma_diff)
        link_blink(link_karma_diff, gpio_plus)
    return

def signal_comment_karma_shift(comment_karma_diff, gpio_plus, gpio_minus):
    if comment_karma_diff < 0:
        print "Comment karma shift %d" % (comment_karma_diff)
        comment_blink(abs(comment_karma_diff), gpio_minus)
    elif comment_karma_diff > 0:
        print "Comment karma shift %d" % (comment_karma_diff)
        comment_blink(comment_karma_diff, gpio_plus)
    return

user_agent = "linux:Karma Watch:v0.0.1 (by /u/not_da_bot)"

username = get_arg_user()
r = init_reddit(user_agent, cachetime=1)
user = r.get_redditor(username)
link_karma = user.link_karma
comment_karma = user.comment_karma

gpio_plus = 40
gpio_minus = 37
gpio_list = [gpio_plus, gpio_minus]

print "Karma watch start link : %d comment : %d" % (link_karma, comment_karma)

try:
    init_gpio(gpio_list)
    import pprint
    while 1:
        pprint.pprint("dir(user)")
        pprint.pprint(dir(user))
        pprint.pprint("vars(user)")
        pprint.pprint(vars(user))
        pprint.pprint("dir(r)")
        pprint.pprint(dir(r))
        pprint.pprint("vars(r)")
        pprint.pprint(vars(r))
        exit(1)
        tlink_karma = user.link_karma
        tcomment_karma = user.comment_karma
        link_karma_diff = tlink_karma - link_karma
        comment_karma_diff = tcomment_karma - comment_karma
        signal_link_karma_shift(link_karma_diff, gpio_plus, gpio_minus)
        signal_comment_karma_shift(comment_karma_diff, gpio_plus, gpio_minus)
        link_karma = tlink_karma
        comment_karma = tcomment_karma
        time.sleep(1)
except KeyboardInterrupt:
    print >> sys.stderr, "\nKeyboard Interruption\n"
except praw.errors.InvalidUserPass:
    print >> sys.stderr, "\nInvalid credentials\n"
except Exception,e:
    print >> sys.stderr, "\nUnexpected Exception\n"
    print >> sys.stderr, str(e)
finally:
    GPIO.cleanup()
    print >> sys.stderr, "Bye"
