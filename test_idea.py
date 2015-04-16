#!/usr/bin/python
#
#Little test to try out the linear algebra idea for hash functions

import numpy, os, fileinput, copy, random
import matplotlib.pyplot as plt

# A helper function... creates a 1-D matrix of "x" raised from powers 0 to "power"
def power_matrix(x, power):
    vals = []
    for i in range(power):
        vals.append(x**i)
    return numpy.array(vals)

# a tedious function that solves the polynomial equation
# I made it to more easily debug what was going on... rather than just do the dot-product
def walk_eq(x_matrix, coeff_matrix):

    return numpy.dot(x_matrix, coeff_matrix)
    #Comment the above line if you want to see the calculations walked-through verbosely
    
    # result_string_1 = []
    # result_string_2 = []
    # result = 0.0
    # print "x_matrix = %s" % str(x_matrix)
    # print "coeff_matrix = %s" % str(coeff_matrix)
    # for i in range(len(x_matrix)):
    #     result_string_1.append(str(coeff_matrix[i]))
    #     result_string_1.append('*')
    #     result_string_1.append(str(x_matrix[i]))
    #     result_string_2.append(str(coeff_matrix[i] * x_matrix[i]))
    #     result += (coeff_matrix[i]*x_matrix[i])
    #     if i < (len(x_matrix)-1):
    #         result_string_1.append(' + ')
    #         result_string_2.append(' + ')
    # print "--> %s" % ''.join(result_string_1)
    # print "--> %s" % ''.join(result_string_2)
    # print "--> %s" % str(result)
    # test_result = numpy.dot(x_matrix, coeff_matrix)
    # if test_result- result > .0000001:
    #     raise Exception("walk_eq func did not equal the dot product!")
    # return result

# give it a key-value list and it returns a hash function!
# actually, returns the coefficient matrix to use...
def gimme_hash_function(key_list, value_list):

    hash_value_count = len(key_list)
    hash_value_array = numpy.array(value_list)
    exponented_value_list = range(hash_value_count)
    equation_list = []
    power_list = range(hash_value_count)
    #print "Values to hash:"
    #print key_list

    # Making the matrix so we can do least squares solving
    for key in key_list:
        for exp in power_list:
            exponented_value_list[exp] = key**(exp)
        equation_list.append(copy.copy(exponented_value_list))
    
    exp_eq_array = numpy.array(equation_list)

    answer = numpy.linalg.lstsq(exp_eq_array,hash_value_array)
    coeff_matrix = answer[0]
    #print "Coefficient matrix is:"
    #print coeff_matrix
    return coeff_matrix


if __name__=="__main__":

    MODE = "BATCH" # can be either SINGLE or BATCH... SINGLE lets you do an individual run in detail.


    if MODE == "BATCH":
        # get the below to work, then iterate over it by varying set size and max hash value
        batch_size = 10000 # number of runs to try
        set_size = 10 # size of your hash set
        max_key_value = 100 # your upper bound for value size

        hash_success = 0
        hash_failure = 0
        hash_records = []
        hash_value_list = range(set_size)
        bad_records = []

        print "Starting batches..."
        for run_num in range(batch_size):
            run_record = []
            key_list = random.sample(xrange(1,max_key_value+1), set_size)
            key_list.sort()
            coeff_matrix = gimme_hash_function(key_list, hash_value_list)

            run_record.append("#%04d: %s -->" % (run_num, str(key_list)))
            
            # TEST SUCCESS (I really should make this a function)
            # Check to make sure we've been succesful with our function
            new_answer = []
            for i in key_list:
                new_answer.append(walk_eq(power_matrix(i,len(key_list)), coeff_matrix))

            hash_function_works = "TRUE"

            extra_run_string = []
            for i in range(len(new_answer)):
                extra_run_string.append("\n[%3d]-->[%.3f]" % (key_list[i], new_answer[i]))
                if abs(new_answer[i] - hash_value_list[i]) >= .5:
                    extra_run_string.append("  !! FAILURE!")
                    hash_function_works = "FALSE"
                    print "Bad hash at [%d] :( check your file!" % run_num
            run_record.append(''.join(extra_run_string))

            if hash_function_works == "TRUE":
                hash_success = 1 + hash_success
                run_record.append(" hashed succesfully!")
            else:
                hash_failure = 1 + hash_failure
                bad_records.append(run_num)                


            run_record.append("\nfails=%s, succeeeds=%s\n" % (hash_failure, hash_success))
            hash_records.append(''.join(run_record))
            # END TEST SUCCESS


        # Write out the results to a file
        report_file_name = "report_file_size_%s.txt" % set_size
        print "Writing file [%s]" % report_file_name
        report_file = open(report_file_name, 'w')
        header_line = "SET SIZE-->[%s]  MAX KEY VALUE-->[%s]  SUCCESS RATE-->[%d%%]\n" % (set_size, max_key_value, 100*(hash_success/(batch_size*1.0)))
        report_file.write(header_line)
        if(hash_failure>0):
            report_file.write("BAD RUNS: %s\n" % bad_records)

        print "Success rate of %d%%" % (100.0 * (hash_success/(batch_size * 1.0)))

        for line in hash_records:
            report_file.write(line)
        report_file.close()
        print "File written."

        # Just a good little assertion
        if (hash_failure + hash_success) != batch_size:
            print "hash success: [%s] hash failure: [%s]" % (hash_success, hash_failure)
            raise Exception("Accounting went wrong somewhere - batch runs are misaligned!")


    elif MODE == "SINGLE":

        hash_value_count = 10

        # Setting up the values we want to hash
        key_list = random.sample(xrange(1, 101), 10)
        key_list.sort()
        hash_value_list = range(len(key_list))
        coeff_matrix = gimme_hash_function(key_list, hash_value_list)

        new_answer = []
        for i in key_list:
            new_answer.append(walk_eq(power_matrix(i,len(key_list)), coeff_matrix))
        print "Answers produced by the hash function are: "
        print new_answer
    
        # TEST SUCCESS
        # Check to make sure we've been succesful with our function
        hash_function_works = "TRUE"
        for i in range(len(new_answer)):
            if abs(new_answer[i] - hash_value_list[i]) >= .5:
                print "[%s] should map to [%s], but instead maps to [%s]!" % (key_list[i], hash_value_list[i], new_answer[i])
                hash_function_works = "FALSE"
                #raise Exception("Function did not hash successfully!!")
        if hash_function_works == "TRUE":
            print "Function hashed succesfully!"
        # END TEST SUCCESS

        # PLOT THE CURVE
        # The below section actually plots the quadratic equation we created
        fitted_line_values = [x / 10.0 for x in range(1, 10*(max(key_list)+5), 1)]
        fitted_line_answers = []
        for i in fitted_line_values:
            fitted_line_answers.append(walk_eq(power_matrix(i,hash_value_count), coeff_matrix))
        plt.plot(key_list, hash_value_list, 'o', label='Original data', markersize=10)
        plt.plot(fitted_line_values, fitted_line_answers, 'r', label="Hash function line")
        plt.legend(loc=0, numpoints = 1)
        plt.show()
        # END PLOT THE CURVE (I know, this should really be encapsulated into a function)

    else:
        raise Exception("Incorrect operating mode!")

