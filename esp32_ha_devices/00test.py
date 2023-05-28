from c_devices import MultipleController
import time

def test_four_relay_controller():
   
    relay_pins = [4,16]
    controller = MultipleController(relay_pins)
    '''
    controller.turn_on_all_relays()
    time.sleep(2)
    controller.turn_off_all_relays()
    time.sleep(1)
    for i in range(1, len(relay_pins) + 1):
        controller.set_relay_state(i,1)
        time.sleep(2)
        controller.set_relay_state(i,0)
    '''
    controller.turn_off_all_relays()
    controller.set_relay_state(1,1)

    print('所有继电器状态为: ' + str(controller.state))
    time.sleep(2)
    controller.toggle_all_relays()

def main():
    test_four_relay_controller()

if __name__ == "__main__":
    main()   