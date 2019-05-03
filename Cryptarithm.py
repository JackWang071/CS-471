import random

class Puzzle:
    # =====================================================================
    def __init__(self, difficulty=1, operation=0, auto_solve='-ms', test_show_details='-n'):
        def assign_values(op1, op2, ans, middle):
            op1 = str(op1); op2 = str(op2); ans = str(ans)
            vals_list = {'_': ' '}
            lett_list = {'0': [0]}
            available_letters = 'ABCDEFGHIJ'
            lett_i = 0
            # Assigning values to letters
            for c in (op1 + op2 + ans):
                if c not in vals_list:
                    lett_list[available_letters[lett_i]] = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
                    vals_list[c] = available_letters[lett_i]
                    lett_i += 1
            if middle is not None:
                for num in middle:
                    for n in num:
                        if n != '_' and n not in vals_list:
                            lett_list[available_letters[lett_i]] = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
                            vals_list[n] = available_letters[lett_i]
                            lett_i += 1

            return lett_list, vals_list

        def printable_puzzle(operation, op1, op2, ans, middle, vals_list):
            printout = [operation, '', '', '']
            for n in op1:
                printout[1] += vals_list[n]
            for n in op2:
                printout[2] += vals_list[n]
            for n in ans:
                printout[3] += vals_list[n]
            if operation > 2:
                start = 0 if operation == 3 else 1
                for mp in range(start, middle.__len__()):
                    mid_prod_puzz = ''
                    for n in range(middle[mp].__len__()):
                        mid_prod_puzz += vals_list[middle[mp][n]]
                    printout.append(mid_prod_puzz)
            return printout

        def addsub_graph(operation, op1, op2, ans):
            op1 = str(op1) ; op2 = str(op2) ; ans = str(ans)
            lett_list, vals_list = assign_values(op1, op2, ans, None)
            full_puzz = printable_puzzle(operation, op1, op2, ans, None, vals_list)
            # Building the initial graph
            graph_struct = []
            graphwidth = max([op1.__len__(), op2.__len__(), ans.__len__()])
            for i in range(graphwidth):
                if operation == 1:
                    operation = '+'
                else:
                    operation = '-'
                constraint = [operation, '0', '0', '0', 'c' + str(i), 'c' + str(i+1)]
                if i < op1.__len__():
                    constraint[1] = vals_list[op1[-1 - i]]
                if i < op2.__len__():
                    constraint[2] = vals_list[op2[-1 - i]]
                if i < ans.__len__():
                    constraint[3] = vals_list[ans[-1 - i]]
                lett_list['c' + str(i)] = [0, 1]
                graph_struct.append(constraint)
            lett_list['c' + str(graphwidth)] = [0]
            return graph_struct, lett_list, full_puzz

        def mult_graph(op1, op2, ans, middle_prod):
            op1 = str(op1); op2 = str(op2); ans = str(ans)
            lett_list, vals_list = assign_values(op1, op2, ans, middle_prod)
            full_puzz = printable_puzzle(3, op1, op2, ans, middle_prod, vals_list)
            # Building initial graph
            graph_struct = []
            for n in range(op2.__len__()):  # Multiplication constraints
                for n2 in range(op1.__len__()):
                    constraint = ['*', vals_list[op1[-1-n2]], vals_list[op2[-1-n]], vals_list[middle_prod[n][-1-(n+n2)]], 'c' + str(n2) + str(n), 'c' + str(n2 + 1) + str(n)]
                    lett_list['c' + str(n2) + str(n)] = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
                    graph_struct.append(constraint)
                # Add constraint to handle any additional carries on the product
                # (i.e. 24 * 5 = 120, this deals with 120's hundreds place)
                if middle_prod[n].__len__() > op1.__len__() + n:
                    graph_struct.append(['+', '0', '0', vals_list[middle_prod[n][0]], 'c' + str(op1.__len__()) + str(n), '0'])
                    lett_list['c' + str(op1.__len__()) + str(n)] = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
                else:
                    lett_list['c' + str(op1.__len__()) + str(n)] = [0]
            for n in range(ans.__len__()):  # Middle-product addition constraints
                constraint = ['+']  # Adding the operation of this constraint
                for num in middle_prod:
                    # If the current digits place does not exceed the current middle-product's highest digits place:
                    if n >= num.__len__() or num[-1-n] == '_':
                        constraint.append('0')
                    else:
                        constraint.append(vals_list[num[-1-n]])
                constraint.append(vals_list[ans[-1-n]])
                constraint.append('cm' + str(n))
                constraint.append('cm' + str(n+1))
                lett_list['cm' + str(n)] = [i for i in range(0, middle_prod.__len__())]
                graph_struct.append(constraint)
            lett_list['cm' + str(ans.__len__())] = [0]  # Adding the very last carry-out value, which must be zero.

            return graph_struct, lett_list, full_puzz

        def dvd_graph(op1, op2, ans, middle_quot):
            op1 = str(op1); op2 = str(op2); ans = str(ans)
            lett_list, vals_list = assign_values(op1, op2, ans, middle_quot)
            full_puzz = printable_puzzle(4, op1, op2, ans, middle_quot, vals_list)
            # Building graph
            graph_struct = []
            for n in range(ans.__len__()):  # Multiplication constraints
                mq = ((n + 1) * 2) - 1
                for n2 in range(op2.__len__()):
                    # Calculates how many zeroes that must be skipped (i.e. 24 * 500 = 12000, skip last two zeroes)
                    constraint = ['*', vals_list[op2[-1-n2]], vals_list[ans[n]], vals_list[middle_quot[mq][n - ans.__len__() - n2]],
                                  'c' + str(n2) + str(n), 'c' + str(n2 + 1) + str(n)]
                    lett_list['c' + str(n2) + str(n)] = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
                    graph_struct.append(constraint)
                # Add constraint to handle any additional carries on the product
                # (i.e. 24 * 5 = 120, this deals with 120's hundreds place)
                if middle_quot[mq].__len__() > (op2.__len__() + ans.__len__()) - (1 + n):
                    graph_struct.append(['+', '0', '0', vals_list[middle_quot[mq][0]], 'c' + str(op2.__len__()) + str(n), '0'])
                    lett_list['c' + str(op2.__len__()) + str(n)] = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
                else:
                    lett_list['c' + str(op2.__len__()) + str(n)] = [0]

            qi = 2  # represents each subtraction sub-equation in the middle quotients
            while qi < middle_quot.__len__():
                for n in range(middle_quot[qi - 2].__len__()):
                    constraint = ['-', vals_list[middle_quot[qi - 2][-1-n]], '0', '0']
                    if n < middle_quot[qi - 1].__len__() and middle_quot[qi - 1][-1-n] != '_':
                        constraint[2] = vals_list[middle_quot[qi - 1][-1-n]]
                    if n < middle_quot[qi].__len__() and middle_quot[qi][-1-n] != '_':
                        constraint[3] = vals_list[middle_quot[qi][-1-n]]
                    constraint.append('cm' + str(n) + str(qi))
                    constraint.append('cm' + str(n + 1) + str(qi))
                    lett_list['cm' + str(n) + str(qi)] = [0, 1]
                    graph_struct.append(constraint)
                lett_list['cm' + str(middle_quot[qi - 2].__len__()) + str(qi)] = [0]
                qi += 2

            return graph_struct, lett_list, full_puzz

        # Puzzle initializer begins here.
        if 1 > operation > 4:
            operation = random.randint(1,4)

        adjusted_difficulty = difficulty + 2
        if operation == 3:
            adjusted_difficulty = int((difficulty + 4 + operation) / operation)

        operand1 = int(random.randint(0, 10**adjusted_difficulty))
        operand2 = int(random.randint(0, 10**adjusted_difficulty))

        #if operation == 3:
        #    operand1 = 468
        #    operand2 = 72
        if operation == 4:
            operand1 = 9024
            operand2 = 24

        if operation == 1:
            answer = int(operand1 + operand2)
            self.graph, self.letters_list, self.fullpuzzle = addsub_graph(operation, operand1, operand2, answer)
        elif operation == 2:
            while operand1 < operand2:
                operand2 = random.randint(0, 10**(difficulty+2))
            answer = int(operand1 - operand2)
            self.graph, self.letters_list, self.fullpuzzle = addsub_graph(operation, operand1, operand2, answer)
        elif operation == 3:
            answer = int(operand1 * operand2)
            middle_products = []
            op2_tostr = str(operand2)
            # Find the middle products.
            if op2_tostr.__len__() > 1:
                for c in range(op2_tostr.__len__()):
                    mid_p = str(operand1 * int(op2_tostr[-1-c]))
                    for i in range(c):
                        mid_p += '_'
                    middle_products.append(mid_p)

            self.graph, self.letters_list, self.fullpuzzle = mult_graph(operand1, operand2, answer, middle_products)

        else:
            while operand1 % operand2 != 0:
                operand2 = random.randint(1, 10**(difficulty+2))
            answer = int(operand1 / operand2)

            ans_tostr = str(answer)
            middle_quotients = [str(operand1)]
            # Find the middle quotients
            for c in range(ans_tostr.__len__()):
                mid_q = str(operand2 * int(ans_tostr[c]))
                mid_q_zeros = (10**(ans_tostr.__len__() - (c + 1))) * operand2 * int(ans_tostr[c])
                for i in range(ans_tostr.__len__() - (c + 1)):
                    mid_q += '_'
                middle_quotients.append(str(mid_q))
                middle_quotients.append(str(int(middle_quotients[2 * c]) - mid_q_zeros))

            self.graph, self.letters_list, self.fullpuzzle = dvd_graph(operand1, operand2, answer, middle_quotients)

        self.base_letters_list = {}
        for each_letter in self.letters_list:
            self.base_letters_list[each_letter] = [each_val for each_val in self.letters_list[each_letter]]
        self.solve_mode = auto_solve
        self.test_mode = test_show_details

        if self.test_mode == '-t':
            print('Testing: ' + str(operand1) + ' ' + str(operand2) + ' ' + str(answer))
            for arc in self.graph:
                print(arc)

    # =====================================================================
    def nextMove(self):
        def completed():
            # A completed puzzle should have a single value assigned to each variable, including '0' and carries.
            for k in self.letters_list.keys():
                if k != '0' and 'c' not in k and self.letters_list[k].__len__() > 1:
                    return 0

            op1 = ''.join([str(self.letters_list[c][0]) for c in self.fullpuzzle[1]])
            op2 = ''.join([str(self.letters_list[c][0]) for c in self.fullpuzzle[2]])
            ans = ''.join([str(self.letters_list[c][0]) for c in self.fullpuzzle[3]])

            if self.fullpuzzle[0] == 1:
                return 1 if int(op1) + int(op2) == int(ans) else 0
            elif self.fullpuzzle[0] == 2:
                return 1 if int(op1) - int(op2) == int(ans) else 0
            elif self.fullpuzzle[0] == 3:
                return 1 if int(op1) * int(op2) == int(ans) else 0
            else:
                return 1 if int(op1) / int(op2) == int(ans) else 0

        if self.solve_mode == '-as':
            return self.auto_solver()

        assignment = input('Assign a digit to a letter: ')

        # Option to de-assign all letters.
        if assignment == '-':
            for each_letter in self.base_letters_list:
                self.letters_list[each_letter] = [each_val for each_val in self.base_letters_list[each_letter]]
            p.printPuzzle()
            return 0
        # Option to give up.
        if assignment == 'q' or assignment == 'Q':
            return 2
        # Ensuring that the user input is correct.
        try:
            if assignment.__len__() == 2 and assignment[0] in self.letters_list:
                if self.alldiff(assignment, self.letters_list) == 0:
                    print('Another letter has already been assigned the value ' + assignment[1])
                    return 0
        except:
            print('Invalid user input.')
            return 0

        # Running AC-3 algorithm
        result_letters_list = self.ac3_algo(assignment, self.letters_list.copy())
        if result_letters_list is None:
            print('This input renders the puzzle unsolvable.')
            if self.test_mode == '-t':
                print()
                p.printPuzzle()
            return 0
        else:
            self.letters_list = result_letters_list.copy()
            p.printPuzzle()
            return completed()

    # =====================================================================
    def alldiff(self, assignment, lett_list):
        # If the intended value is no longer in the letter's domain of possible values:
        for letter in lett_list:
            if letter != '0' and lett_list[letter].__len__() == 1 and lett_list[letter][0] == int(assignment[1]):
                return 0
        return 1

    # =====================================================================
    def auto_solver(self):
        print()
        print('Auto-solver active.')
        for letter in self.letters_list:
            if letter != '0' and 'c' not in letter:
                for value in self.letters_list[letter]:
                    assignment = letter + str(value)
                    result_letters_list = self.ac3_algo(assignment, self.letters_list.copy())
                    if result_letters_list is not None:
                        self.letters_list = result_letters_list.copy()

                        solved = 1
                        for k in self.letters_list.keys():
                            if k != '0' and 'c' not in k and self.letters_list[k].__len__() > 1:
                                solved = 0

                        if solved == 1:
                            self.printPuzzle()
                            return 1

                        break
        return 0

    # =====================================================================
    def ac3_algo(self, assignment, assigned_letters):
        def check_constraint(const, lett_sublist):
            op1 = const[1]; op2 = const[2]; ans = const[-3]; cin = const[-2]; cout = const[-1]
            if const[0] == '+':
                sum = 0 + lett_sublist[cin]  # starts off with the carry-in value
                for i in range(1, const.__len__() - 3):
                    sum += lett_sublist[const[i]]
                return 1 if sum == lett_sublist[ans] + (10 * lett_sublist[cout]) else 0
            elif const[0] == '-':
                difference = (lett_sublist[op1] - lett_sublist[cin] + (10 * lett_sublist[cout])) - lett_sublist[op2]
                return 1 if difference == lett_sublist[ans] else 0
            elif const[0] == '*':
                product = (lett_sublist[op1] * lett_sublist[op2]) + lett_sublist[cin]
                return 1 if product == lett_sublist[ans] + (10 * lett_sublist[cout]) else 0

        def find_unique(lett, lett_value, const, lett_list, l_sublist):
            const_lets = []
            for i in range(1, const.__len__()-2):
                if const[i] != lett and const[i] != '0' and const[i] not in const_lets:
                    const_lets.append(const[i])

            # Each element in the stack is a copy of the other constraint letters' domains, minus the value assigned to the current variable.
            stack = [[[each_val for each_val in lett_list[each_lett] if each_val != lett_value or 'c' in lett] for each_lett in const_lets]]
            carryin_domain = lett_list[const[-2]].copy() if const[-2] not in l_sublist else [l_sublist[const[-2]]]
            carryout_domain = lett_list[const[-1]].copy() if const[-1] not in l_sublist else [l_sublist[const[-1]]]

            for each_domain in stack[0]:
                # If this assigned value cannot be used without emptying the domain of another letter:
                if each_domain.__len__() == 0:
                    return None

            # Conducting DFS to find a set of values that satisfies the constraint
            while stack.__len__() > 0:
                domain_set = stack[-1]
                stack.pop(-1)
                single_values = []
                unique_values = []
                for d_set in range(domain_set.__len__()):
                    if domain_set[d_set].__len__() > 1:
                        for val in domain_set[d_set]:
                            new_domain_set = single_values.copy()
                            new_domain_set.append([val])
                            for other_dset in range(d_set + 1, domain_set.__len__()):
                                new_domain_set.append(domain_set[other_dset])
                            stack.append(new_domain_set)
                        break  # No need to continue looking through this domain set
                    else:
                        single_values.append([domain_set[d_set][0]])
                        if domain_set[d_set][0] not in unique_values:
                            unique_values.append(domain_set[d_set][0])

                # If a combination of unique values has been found:
                if unique_values.__len__() == domain_set.__len__():
                    # Assigning these values to the letters in the constraint.
                    for ci in range(const_lets.__len__()):
                        l_sublist[const_lets[ci]] = unique_values[ci]
                    # Checking different combinations of values for carry-in and carry-out
                    for cin in carryin_domain:
                        for cout in carryout_domain:
                            l_sublist[const[-1]] = cout
                            l_sublist[const[-2]] = cin
                            if check_constraint(const, l_sublist) == 1:  # If the arc is consistent, success!
                                return l_sublist

            return None  # returns None if no combination of values can make the arc consistent

        def arc_reduce(lett_index, const, lett_list):
            if self.solve_mode == '-as' or self.test_mode == '-t':
                print('Arc: ' + const[lett_index] + ' ' + str(const))
            lett = const[lett_index]
            # Check that each value in this letter's domain is arc-consistent.
            for dv in range(lett_list[lett].__len__()):
                l_sublist = {'0': 0, lett: lett_list[lett][dv]}  # initialize sublist with 0 and the current value in this letter's domain
                l_sublist = find_unique(lett, lett_list[lett][dv], const, lett_list, l_sublist)  # must find a combination of unique values for any undefined variables
                # Checking if this set of values can satisfy the constraint.
                # If the letter is assigned this value and the constraint is still unsolvable, mark the value for removal.
                if l_sublist is None:
                    if self.solve_mode == '-as' or self.test_mode == '-t':
                        print('Delete: ' + str(lett_list[lett][dv]) + ' from ' + lett + ' ' + str(const))
                    lett_list[lett][dv] = -1
            return lett_list

        # AC-3 algorithm begins
        assigned_letters[assignment[0]] = [int(assignment[1])]  # Assigning value to this letter

        # Make a copy of the letters' domains, for ease of modification
        letter_list = {}
        for each_letter in assigned_letters:
            letter_list[each_letter] = [v for v in assigned_letters[each_letter]]
        for k in letter_list:
            # Remove the assigned value from the domain of the other letters.
            if k != '0' and 'c' not in k and k != assignment[0] and int(assignment[1]) in letter_list[k]:
                letter_list[k].remove(int(assignment[1]))

        # Building the examination queue.
        exam_queue = []
        for constraint in self.graph:
            # Adds all possible arcs to the examination queue
            for v in range(1, constraint.__len__()):
                if constraint[v] != '0':
                    exam_queue.append([v, constraint])

        while exam_queue.__len__() > 0:
            constraint = exam_queue[0][1]
            letter_index = exam_queue[0][0]
            exam_queue.pop(0)
            letter_list = arc_reduce(letter_index, constraint, letter_list)
            # If this letter's domain has been reduced:
            if -1 in letter_list[constraint[letter_index]]:
                this_letter = constraint[letter_index]
                letter_list[this_letter] = [x for x in letter_list[this_letter] if x != -1]
                # If a letter's domain is reduced to empty, then the puzzle cannot be solved.
                if letter_list[this_letter].__len__() == 0:
                    if self.test_mode == '-t':
                        print(self.letters_list)
                        print(letter_list)
                    return None
                # Otherwise add arcs that terminate at the current letter to the exam queue
                for this_const in self.graph:
                    if constraint[letter_index] in this_const:
                        for v_in in range(1, this_const.__len__()):
                            if constraint[letter_index] != this_const[v_in] and this_const[v_in] != '0':
                                exam_queue.append([v_in, this_const])

        if self.solve_mode == '-as':
            print(self.letters_list)
            return letter_list

        return assigned_letters

    # =====================================================================
    def printPuzzle(self):
        def conversion(number):
            new_number = [number_i for number_i in number]
            for number_j in range(new_number.__len__()):
                if new_number[number_j] != ' ' and self.letters_list[new_number[number_j]].__len__() == 1:
                    new_number[number_j] = str(self.letters_list[new_number[number_j]][0])
            return ''.join(new_number)

        operation = self.fullpuzzle[0]
        op1 = self.fullpuzzle[1]
        op2 = self.fullpuzzle[2]
        ans = self.fullpuzzle[3]

        operand1_line = '  '
        operand2_line = '\n  '
        answer_line = '\n  '

        if operation <= 2:
            operand1_line += '  '
            answer_line += '  '
            if operation == 1:
                operand2_line += '+ '
            else:
                operand2_line += '- '
            num_digits = max([op1.__len__(), op2.__len__(), ans.__len__()])
            for n in range(num_digits):
                if n < num_digits - op1.__len__():
                    operand1_line += ' '
                if n < num_digits - op2.__len__():
                    operand2_line += ' '
                if n < num_digits - ans.__len__():
                    answer_line += ' '

            operand1_line += conversion(op1)
            operand2_line += conversion(op2)
            answer_line += conversion(ans)

            separator = '\n'
            for i in range(operand2_line.__len__()-1):
                separator += '-'

            print(operand1_line + operand2_line + separator + answer_line)

        elif operation == 3:
            # Print operands and operator.
            for c in range(ans.__len__() - (op1.__len__())):
                operand1_line += ' '
            for c in range(ans.__len__() - (op2.__len__() + 3)):
                operand2_line += ' '
            operand1_line += conversion(op1)
            operand2_line += ('*  ' + conversion(op2))
            answer_line += conversion(ans)
            print(operand1_line + operand2_line)
            # Separator lines.
            separator = ''
            for i in range(ans.__len__() + 2):
                separator += '-'
            print(separator)
            # Printing the middle products.
            for n in range(4, self.fullpuzzle.__len__()):
                number = '  '
                # Calculating how many spaces are needed to properly line up this number.
                for c in range(ans.__len__() - (self.fullpuzzle[n].__len__())):
                    number += ' '
                number += conversion(self.fullpuzzle[n])
                print(number)

            print(separator + answer_line)

        elif operation == 4:
            operands_line = '\n  ' + conversion(op2) + ' | ' + conversion(op1)
            answer_line = ''
            positioning_spaces = ''

            # Correctly positioning the quotient
            for c in range(operands_line.__len__()):
                if c < operands_line.index('|') - 1:
                    positioning_spaces += ' '
                if c < operands_line.__len__() - ans.__len__() - 1:
                    answer_line += ' '
            answer_line += conversion(ans)

            separator = positioning_spaces + ''
            for i in range(op1.__len__() + 2):
                separator += '-'

            print(answer_line + '\n' + separator + operands_line)

            for n in range(4, self.fullpuzzle.__len__()):
                midq = positioning_spaces + ''
                for s in range(op1.__len__() - self.fullpuzzle[n].__len__()):
                    midq += ' '
                if n % 2 == 0:
                    midq += ('- ')
                else:
                    print(separator)
                    midq += ('  ')
                midq += conversion(self.fullpuzzle[n])
                print(midq)

# =============================================================================================================

difficulty_level = input('Please enter a difficulty (1-9): ')
s_mode = '-ms'
if '-as' in difficulty_level:
    s_mode = '-as'
t_mode = '-n'
if '-t' in difficulty_level:
    t_mode = '-t'

p = Puzzle(int(difficulty_level[0]), operation=3, auto_solve=s_mode, test_show_details=t_mode)

repeat = 0
p.printPuzzle()

print()
print('Example input: A2, to assign digit 2 to letter A. Enter Q to quit.')
while repeat == 0:
    print()
    repeat = p.nextMove()
    if repeat == 2:
        print('Exiting puzzle.')
    elif repeat == 1:
        print('Puzzle solved!')
