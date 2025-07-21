from collections import defaultdict

errors = {}

errors['price'] = "Error in price command. Usage: $price <symbol>. Example: $price eth"
errors['long'] = "Error in long command. Usage: $long <symbol> <$amount in dollars / amount in tokens> <leverage>. Example: $long eth $10000 5, or $long eth 3 5"
errors['short'] = "Error in short command. Usage: $short <symbol> <$amount in dollars / amount in tokens> <leverage>. Example: $short eth $10000 5, or $long eth 3 5"
errors['buy'] = "Error in buy command. Usage: $buy <symbol> <$amount in dollars / amount in tokens>. Example: $buy eth $3000, or $buy eth 1"
errors['sell'] = "Error in sell command. Usage: $sell <symbol> <$amount in dollars / amount in tokens>. Example: $sell eth $3000, or $sell eth 1"
errors['close'] = "Error in close command. Usage: $close <position ID>. Example: $close 1. Position ID can be found in front of your position in $port."

def get_error_message(command):
    return errors[command]