import argparse
import sys
import time
#import RPi.GPIO as GPIO
import json
from urllib2 import urlopen

def get_arg_user():
    argparser = argparse.ArgumentParser()
    argparser.add_argument("username")
    args = argparser.parse_args()
    return args.username

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

def get_user_about(username):
    url = "https://www.reddit.com/user/%s/about.json" % username
    response = urlopen(url)
    return json.load(response)

username = get_arg_user()
about = get_user_about(username)
link_karma = about[u'data'][u'link_karma']
comment_karma = about[u'data'][u'comment_karma']

gpio_plus = 40
gpio_minus = 37
gpio_list = [gpio_plus, gpio_minus]

print "Karma watch start link : %d comment : %d" % (link_karma, comment_karma)

try:
    init_gpio(gpio_list)
    while 1:
        time.sleep(5)
        about = get_user_about(username)
        tlink_karma = about[u'data']["link_karma"]
        tcomment_karma = about[u'data']["comment_karma"]
        link_karma_diff = tlink_karma - link_karma
        comment_karma_diff = tcomment_karma - comment_karma
        signal_link_karma_shift(link_karma_diff, gpio_plus, gpio_minus)
        signal_comment_karma_shift(comment_karma_diff, gpio_plus, gpio_minus)
        link_karma = tlink_karma
        comment_karma = tcomment_karma
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
