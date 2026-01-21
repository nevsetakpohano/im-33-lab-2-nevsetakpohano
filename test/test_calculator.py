import pytest
import tempfile
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from calculator import (
    CalculatorState,
    parse_input,
    validate_sequence,
    handle_keypress,
    calculate,
    process_file
)


def test_calculator_state_initialization():
    state = CalculatorState()
    assert state.screen == 0
    assert state.first_number == 0
    assert state.op is None
    assert state.waiting_for_second_number is False
    assert state.last_key is None


def test_calculator_state_repr():
    state = CalculatorState()
    state.screen = 123
    state.first_number = 100
    state.op = "+"
    state.waiting_for_second_number = True
    
    repr_str = repr(state)
    assert "CalculatorState" in repr_str
    assert "screen=123" in repr_str
    assert "first_number=100" in repr_str
    assert "op='+'" in repr_str


def test_parse_input_basic():
    assert parse_input("1 2 + 3 =") == ["1", "2", "+", "3", "="]
    assert parse_input("") == []
    assert parse_input("   ") == []


def test_parse_input_with_multi_digit_numbers():
    assert parse_input("123 + 456 =") == ["1", "2", "3", "+", "4", "5", "6", "="]
    assert parse_input("89 - 55 =") == ["8", "9", "-", "5", "5", "="]


def test_parse_input_edge_cases():
    assert parse_input("5") == ["5"]
    assert parse_input("=") == ["="]
    assert parse_input("1   2   +   3   =") == ["1", "2", "+", "3", "="]


def test_validate_sequence_valid():
    validate_sequence(["1", "2", "+", "3", "="])
    validate_sequence(["5", "="])
    validate_sequence(["1", "+", "2", "="])
    validate_sequence(["1", "2", "3"])


def test_validate_sequence_invalid_start():
    with pytest.raises(ValueError):
        validate_sequence(["+", "1", "="])


def test_validate_sequence_invalid_after_first_number():
    with pytest.raises(ValueError):
        validate_sequence(["1", "x", "="])


def test_validate_sequence_invalid_after_operator():
   
    with pytest.raises(ValueError):
        validate_sequence(["1", "+", "+"])
    
    with pytest.raises(ValueError):
        validate_sequence(["1", "+", "+", "="])


def test_handle_keypress_digits():
    state = CalculatorState()
    
    handle_keypress(state, "5")
    assert state.screen == 5
    assert state.last_key == "5"
    
    handle_keypress(state, "6")
    assert state.screen == 56


def test_handle_keypress_operations():
    state = CalculatorState()
    
    handle_keypress(state, "1")
    handle_keypress(state, "2")
    handle_keypress(state, "+")
    assert state.first_number == 12
    assert state.op == "+"
    assert state.waiting_for_second_number is True
    
    handle_keypress(state, "3")
    assert state.screen == 3
    assert state.waiting_for_second_number is False
    
    handle_keypress(state, "4")
    handle_keypress(state, "=")
    assert state.screen == 46


def test_handle_keypress_all_operations():
    state = CalculatorState()
    handle_keypress(state, "1")
    handle_keypress(state, "0")
    handle_keypress(state, "+")
    handle_keypress(state, "2")
    handle_keypress(state, "0")
    handle_keypress(state, "=")
    assert state.screen == 30
    
    state = CalculatorState()
    handle_keypress(state, "5")
    handle_keypress(state, "0")
    handle_keypress(state, "-")
    handle_keypress(state, "3")
    handle_keypress(state, "0")
    handle_keypress(state, "=")
    assert state.screen == 20
    
    state = CalculatorState()
    handle_keypress(state, "6")
    handle_keypress(state, "*")
    handle_keypress(state, "7")
    handle_keypress(state, "=")
    assert state.screen == 42
    
    state = CalculatorState()
    handle_keypress(state, "1")
    handle_keypress(state, "0")
    handle_keypress(state, "0")
    handle_keypress(state, "/")
    handle_keypress(state, "2")
    handle_keypress(state, "5")
    handle_keypress(state, "=")
    assert state.screen == 4


def test_handle_keypress_division_by_zero():
    state = CalculatorState()
    
    handle_keypress(state, "5")
    handle_keypress(state, "/")
    handle_keypress(state, "0")
    
    with pytest.raises(ZeroDivisionError):
        handle_keypress(state, "=")


def test_handle_keypress_integer_division():
    state = CalculatorState()
    
    handle_keypress(state, "9")
    handle_keypress(state, "/")
    handle_keypress(state, "1")
    handle_keypress(state, "0")
    handle_keypress(state, "=")
    assert state.screen == 0


def test_calculate_examples_from_assignment():
    assert calculate(["0"]) == 0
    assert calculate(["5"]) == 5
    assert calculate(["1", "2"]) == 12
    assert calculate(["1", "2", "3", "+", "4", "5", "6", "="]) == 579
    assert calculate(["1", "2", "3", "-", "2", "3", "="]) == 100
    assert calculate(["1", "0", "-", "1", "0", "0", "="]) == -90
    assert calculate(["1", "0", "*", "2", "2", "="]) == 220
    assert calculate(["1", "0", "0", "/", "3", "="]) == 33
    assert calculate(["9", "/", "1", "0", "="]) == 0
    assert calculate(["1", "2", "3", "+"]) == 123
    assert calculate(["1", "2", "3", "+", "4", "4"]) == 44
    assert calculate(["1", "2", "3", "+", "4", "5", "6"]) == 456


def test_calculate_intermediate_results():
    result = calculate(["1", "2", "3", "+", "4", "5", "6", "="], True)
    assert result == [1, 12, 123, 123, 4, 45, 456, 579]
    
    result = calculate(["1", "0", "0", "/", "3", "="], True)
    assert result == [1, 10, 100, 100, 3, 33]


def test_process_file_success():
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as input_file:
        input_file.write("1 2 3 + 4 5 6 =\n")
        input_path = input_file.name
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as output_file:
        output_path = output_file.name
    
    try:
        process_file(input_path, output_path)
        
        with open(output_path, 'r') as f:
            result = f.read().strip()
        
        assert result == "579"
    finally:
        if os.path.exists(input_path):
            os.unlink(input_path)
        if os.path.exists(output_path):
            os.unlink(output_path)


def test_process_file_invalid_sequence():
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as input_file:
        input_file.write("1 + + 2 =\n")
        input_path = input_file.name
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as output_file:
        output_path = output_file.name
    
    try:
        with pytest.raises(ValueError):
            process_file(input_path, output_path)
    finally:
        if os.path.exists(input_path):
            os.unlink(input_path)
        if os.path.exists(output_path):
            os.unlink(output_path)