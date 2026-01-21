
class CalculatorState:
    
    
    def __init__(self):
        self.screen = 0
        self.first_number = 0
        self.op = None
        self.waiting_for_second_number = False
        self.last_key = None
    
    def __repr__(self):
        return (
            f"CalculatorState(screen={self.screen}, "
            f"first_number={self.first_number}, "
            f"op={repr(self.op)}, "
            f"waiting_for_second_number={self.waiting_for_second_number})"
        )


def parse_input(input_str: str) -> list[str]:
    
    if not input_str:
        return []
    
    parts = input_str.strip().split()
    
    keys = []
    for part in parts:
        if part.isdigit() and len(part) > 1:
            for digit in part:
                keys.append(digit)
        elif part in ["+", "-", "*", "/", "="]:
            keys.append(part)
        else:
            keys.append(part)
    
    return keys


def validate_sequence(keys: list[str]) -> None:
    state = "start"
    
    for i, key in enumerate(keys):
        if state == "start":
            if key.isdigit():
                state = "first_number"
            elif key == "=":
                state = "equals"
            else:
                raise ValueError(f"Expected digit at start, got '{key}'")
                
        elif state == "first_number":
            if key.isdigit():
                continue
            elif key in "+-*/":
                state = "operator"
            elif key == "=":
                state = "equals"
            else:
                raise ValueError(f"Expected digit or operator, got '{key}'")
                
        elif state == "operator":
            if key.isdigit():
                state = "second_number"
            elif key in "+-*/":
                raise ValueError(f"Expected digit after operator, got '{key}'")
            elif key == "=":
                state = "equals"
            else:
                raise ValueError(f"Expected digit or =, got '{key}'")
                
        elif state == "second_number":
            if key.isdigit():
                continue
            elif key == "=":
                state = "equals"
            elif key in "+-*/":
                raise ValueError(f"Expected digit or =, got '{key}'")
            else:
                raise ValueError(f"Expected digit or =, got '{key}'")
                
        elif state == "equals":
            raise ValueError(f"Unexpected key '{key}' after =")
    
  

def handle_keypress(state: CalculatorState, key: str) -> None:
  
    if key.isdigit():
        digit = int(key)
        
        if state.waiting_for_second_number or (state.last_key and state.last_key in "+-*/") or state.last_key is None:
            state.screen = digit
            state.waiting_for_second_number = False
        else:
            state.screen = state.screen * 10 + digit
    
    elif key in "+-*/":
        if state.last_key and state.last_key in "+-*/":
            state.op = key
        else:
            state.first_number = state.screen
            state.op = key
            state.waiting_for_second_number = True
    
    elif key == "=":
        if state.op is not None and not state.waiting_for_second_number:
            if state.op == "+":
                state.screen = state.first_number + state.screen
            elif state.op == "-":
                state.screen = state.first_number - state.screen
            elif state.op == "*":
                state.screen = state.first_number * state.screen
            elif state.op == "/":
                if state.screen == 0:
                    raise ZeroDivisionError("Division by zero")
                state.screen = state.first_number // state.screen
            
            state.op = None
            state.waiting_for_second_number = False
    
    else:
        raise ValueError(f"Invalid key: '{key}'. Valid keys: digits (0-9), operators (+, -, *, /), equals (=)")
    
    state.last_key = key


def calculate(keys: list[str], return_intermediate: bool = False, validate: bool = True):
   
    if validate:
        validate_sequence(keys)
    
    state = CalculatorState()
    intermediate_states = []
    
    for key in keys:
        handle_keypress(state, key)
        intermediate_states.append(state.screen)
    
    if return_intermediate:
        return intermediate_states
    return state.screen


def interactive_calculator():
  
    print("Interactive Calculator")
    print("=" * 40)
    print("Rules:")
    print("- Enter keys separated by spaces")
    print("- Valid keys: digits (0-9), operators (+, -, *, /), equals (=)")
    print("- Format: digits → operator → digits → =")
    print("- Example: '8 5 - 6 3 =' or '89 - 55 ='")
    print("- Enter 'q' to quit")
    print("=" * 40)
    
    while True:
        try:
            user_input = input("\nEnter keys: ").strip()
            if user_input.lower() == 'q':
                print("Goodbye!")
                break
            
            if not user_input:
                continue
            
            try:
                keys = parse_input(user_input)
            except Exception as e:
                print(f"Error parsing input: {e}")
                continue
            
            # Show intermediate states
            print("\nStep-by-step calculation:")
            print("-" * 30)
            state = CalculatorState()
            step = 1
            
            for i, key in enumerate(keys):
                previous_screen = state.screen
                handle_keypress(state, key)
                
                if key.isdigit():
                    action = f"Added digit {key}"
                elif key in "+-*/":
                    action = f"Selected operation {key}"
                else:  # =
                    action = "Pressed equals"
                
                change = ""
                if state.screen != previous_screen:
                    change = f" (changed from {previous_screen})"
                
                print(f"Step {step}: {action:20} -> Screen: {state.screen}{change}")
                step += 1
            
            print("-" * 30)
            print(f"Final result: {state.screen}")
            
        except ValueError as e:
            print(f"Error: {e}")
            print("Valid format example: '8 5 - 6 3 =' or '89 - 55 ='")
        except ZeroDivisionError as e:
            print(f"Error: {e}")
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"Unexpected error: {e}")


def process_file(input_file: str, output_file: str) -> None:
   
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            input_str = f.read().strip()
        
        if not input_str:
            raise ValueError("Input file is empty")
        
        keys = parse_input(input_str)
        validate_sequence(keys) 
        result = calculate(keys)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(str(result))
            
    except FileNotFoundError:
        print(f"Error: Input file '{input_file}' not found.")
        raise
    except (ValueError, ZeroDivisionError) as e:
        print(f"Error in calculation: {e}")
        raise


def main():

    import sys
    
    if len(sys.argv) == 1:
        interactive_calculator()
    elif len(sys.argv) == 4 and sys.argv[1] == "--file":
        input_file = sys.argv[2]
        output_file = sys.argv[3]
        
        try:
            process_file(input_file, output_file)
            print(f"Success! Result written to {output_file}")
            
        except FileNotFoundError:
            print(f"Error: Input file '{input_file}' not found.")
            sys.exit(1)
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)
    elif len(sys.argv) == 2 and sys.argv[1] == "--help":
        print("Calculator - Lab 2 Implementation")
        print("=" * 40)
        print("\nUsage:")
        print("  python calculator.py                     # Interactive mode")
        print("  python calculator.py --file input.txt output.txt  # File mode")
        print("  python calculator.py --help              # Show this help")
        print("\nInteractive mode examples:")
        print("  8 5 - 6 3 =          # 85 - 63 = 22")
        print("  89 - 55 =            # 89 - 55 = 34 (automatically splits to 8 9 - 5 5 =)")
        print("  1 2 3 + 4 5 6 =      # 123 + 456 = 579")
    else:
        print("Invalid arguments. Use --help for usage information.")
        sys.exit(1)


if __name__ == "__main__":
    main()