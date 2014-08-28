/***************************************************************************
Program to print out combinations of gauge blocks to make a particular 
dimension.  The program is specific to inch-sized gauge blocks, but
wouldn't be hard to convert to a program that worked with metric
blocks.

The algorithm used is exhaustive search -- all combinations that sum
to the desired size will be printed.  To limit the search time, set
the combination_limit constant to a small number of blocks.

The number of combinations that will have to be checked are
    
    Sum[from i=1 to k] C(n, i)

where n is the number of blocks in the set and k is the maximum number
of blocks to use.  For an 81 block set, this starts to be an
inconveniently large number of combinations at around k = 6 or 7 on my
computer.

However, the program is of practical use on a reasonably modern computer.
I wrote it because I have a second-hand gauge block set that is missing
a number of blocks.  It is not obvious how to manually select blocks to
make a specific desired size, but the computer can figure it out far
more quickly than I can.

----------------------------------------------------------------------
Note that this gauge block problem is the NP-complete subset sum problem:
http://en.wikipedia.org/wiki/Subset_sum_problem

----------------------------------------------------------------------
Copyright (C) 2006 Don Peterson
donp@gdssw.com

This program is free software; you can redistribute it
and/or modify it under the terms of the GNU General Public
License as published by the Free Software Foundation; either
version 2 of the License, or (at your option) any later
version.

This program is distributed in the hope that it will be
useful, but WITHOUT ANY WARRANTY; without even the implied
warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
PURPOSE.  See the GNU General Public License for more
details.

You should have received a copy of the GNU General Public
License along with this program; if not, write to the Free
Software Foundation, Inc., 59 Temple Place, Suite 330,
Boston, MA 02111-1307  USA
***************************************************************************/

#include <iostream>
#include <string>
#include <cstdlib>
#include <cstdio>
using namespace std;

const int OK            = 0;
const int NotOK         = 1;
const int DONE          = 2;
const int NotDONE       = 3;
const int INIT          = 1;
const int NoINIT        = 0;
const int inches_to_tenths = 10000; // Converts inches to 0.0001" units

int combination_limit = 5;          // No more blocks in a stack than this
string program_name;
bool use_mm   = false;              // Use mm on command line instead of inches
bool show_all = false;              // Show all matches, not just first
bool show_number_combinations = false;   // Show number checked
bool wear_blocks = false;           // If true, use two wear blocks
int wear_block_size = 1000;         // Wear block size in 1e-4 inches

int * sizes;                        // Points to which array to use
int n_sizes = 0;                    // Number of elements in block array

int sizes_don[] = {
    // This array is specific to the author's set of gauge blocks
    // (it was a second-hand set with a number of missing blocks).
     250,  350,  490,  500, 1000, 1003, 1004, 1005, 1006, 1007, 1008,
    1009, 1040, 1050, 1060, 1070, 1080, 1090, 1110, 1120, 1140, 1160,
    1170, 1180, 1190, 1210, 1220, 1230, 1250, 1260, 1270, 1290, 1300,
    1310, 1320, 1330, 1340, 1350, 1370, 1380, 1390, 1400, 1420, 1430,
    1440, 1450, 1460, 1470, 1500, 2500, 3500, 4500, 5500, 6000, 6500,
    7000, 7500, 8000, 8500, 9000, 9500,
    20000, 30000, 40000
};

// This uses a normal 81 block inch set.
//
// This array must be sorted from smallest to largest.  It
// contains the block lengths in integers in 1e-4 inches.
int sizes_81[] = {
    500,  1000, 1001, 1002, 1003, 1004, 1005, 1006, 1007, 1008, 1009,
    1010, 1020, 1030, 1040, 1050, 1060, 1070, 1080, 1090, 1100, 1110,
    1120, 1130, 1140, 1150, 1160, 1170, 1180, 1190, 1200, 1210, 1220,
    1230, 1240, 1250, 1260, 1270, 1280, 1290, 1300, 1310, 1320, 1330,
    1340, 1350, 1360, 1370, 1380, 1390, 1400, 1410, 1420, 1430, 1440,
    1450, 1460, 1470, 1480, 1490, 1500, 2000, 2500, 3000, 3500, 4000,
    4500, 5000, 5500, 6000, 6500, 7000, 7500, 8000, 8500, 9000, 9500,
    10000, 20000, 30000, 40000
};

int sizes_36[] = {
    500,  1001, 1002, 1003, 1004, 1005, 1006, 1007, 1008, 1009,
    1010, 1020, 1030, 1040, 1050, 1060, 1070, 1080, 1090, 1100, 
    1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 1000, 2000, 
    3000, 4000, 5000, 10000, 20000, 40000
};

int GetNextCombination(int n, int k, int reset, int *array)
{
    /***********************************************************************
    The following function came from lex_comb.c by Glenn Rhoads.
    http://remus.rutgers.edu/~rhoads/Code/lex_comb.c
    Slightly modified by DP to use constants for return values rather
    than 0 and 1.
 
    Usage to get the sequential list of combinations of n things take k
    at a time:
 
        // Initialize things
        GetNextCombination(n, k, 1, array);
    
        while (GetNextCombination(n, k, 0, array)) 
        {
            PrintArray(array, k);
        }
 
    The array contains k+1 integers; the first element is ignored so
    that 1-based indexing and numbering can be used.
    ***********************************************************************/
 
    /***********************************************************************
    This function will fill the integer array array with successive values of
    the combinations of (n, k).  It returns NotDONE if the next set of values
    is valid and DONE if all combinations have been delivered.
 
    Set reset to nonzero if you want the routine to start over.
    ***********************************************************************/
    static int ix = 0;
    static int jx = 0;
    static int just_reset = 0;
 
    if (reset != 0) {
        /* Initialization */
        jx = 1;
        array[0] = -1;
        for (ix=1; ix <= k; ix++) {
            array[ix] = ix;
        }
        /* Initialization doesn't indicate that the array is valid */
        just_reset = 1;
        return DONE;
    }
 
    if (jx > 0) {
        if (just_reset != 0) {
            just_reset = 0;
            return NotDONE;
        }
        jx = k;
        while (array[jx] == n - k + jx) {
            jx--;
        }
        if (jx == 0) {
            return DONE;
        }
        array[jx]++;
        for (ix = jx + 1; ix <= k; ix++) {
            array[ix] = array[ix-1] + 1;
            //PrintArray(array, k);
        }
        return NotDONE;
    } else {
        jx = 0;
        return DONE;
    }
}

void Usage(void)
{
    cout << 
"Usage:  " << program_name << " [options] size1 [size2...]\n"
"\n"
"Prints a selection of inch gauge blocks to make a specific length.  By\n"
"default, the program uses the custom set of gauge blocks given in the\n"
"source code.  Use the options to use a standard 36 or 81 block set of\n"
"inch blocks.\n"
"\n"
"The program does an exhaustive search, so it may take a long time and.\n"
"print out lots of combinations of blocks that give the desired size.\n"
"\n"
"Options:\n"
"   -36\n"
"       Use an inch standard 36 block set.\n"
"   -81\n"
"       Use an inch standard 81 block set.\n"
"   -a\n"
"       Show all combinations that give the required size.  The normal\n"
"       behavior is to print out the first match.\n"
"   -k n\n"
"       Change the maximum number of blocks allowed in the\n"
"       set to n.  The default value is " << combination_limit << ".\n"
"   -m\n"
"       Sizes are specified in mm.\n"
"   -n\n"
"       Show number of combinations checked.\n"
"   -s\n"
"       Print out the block sizes being used.\n"
"   -w\n"
"       Include two 0.1000 inch wear blocks in the stack.\n"
"\n"
    ;
}

void CheckInput(char ** args)
{
    if (not *args)
    {
        Usage();
        exit(1);
    }

    // Get sum of lengths of blocks and see if the desired size is too
    // long.
    int sum = 0;
    for (int i=0; i < n_sizes; i++)
    {
        sum += sizes[i];
    }
    double max_size = sum/inches_to_tenths;


    while (*args)
    {
        double size_inches = atof(*args);
        if (use_mm)
            size_inches /= 25.4;
        if (size_inches <= 0.0)
        {
            cerr << *args << " is not a proper size.\n";
            exit(1);
        }
#ifndef TEST
        if (size_inches > max_size)
        {
            cerr << "Requested size " << *args 
                 << " is outside the capability of the blocks = "
                 << max_size << endl;
            exit(1);
        }
#endif
        args++;
    }

}

void PrintResult
(
    const int * const combinations, 
    const int n, 
    const string & size
)
{
    printf("  ");
    for (int i = 1; i <= n; i++)
    {
        int int_value = sizes[combinations[i] - 1];
        double value = double(int_value)/inches_to_tenths;
        printf("%.4f  ", value);
    }
    if (wear_blocks)
        printf("(and two %.4f wear blocks)", 
               double(wear_block_size)/inches_to_tenths);
    cout << "\n";
}

int TestArray
(
    const int * const combinations, 
    const int k, 
    const string & size,
    const int target_size
)
{
    // Return != 0 if we only need to print out one match.
    int sum = 0;
    if (wear_blocks)
        sum = 2*wear_block_size;

    for (int i = 1; i <= k; i++)
    {
        sum += sizes[combinations[i] - 1];
    }
    if (sum == target_size)
    {
        PrintResult(combinations, k, size);
        if (not show_all)
            return 1;
    }
    return 0;
}

void PrintCombination(const int * const combinations, const int size)
{
    for (int i = 1; i <= size; i++)
    {
        cout << combinations[i] << " ";
    }
    cout << "\n";
}

void ConstructBlockSet(const string & size)
{
    string::size_type s = size.find(".");
    int inches   = 0;
    int fraction = 0;
    int target_value = 0;
    if (use_mm)
    {
        target_value = int(atof(size.c_str())/25.4*1e4);
    }
    else
    {
        if (s == string::npos)
        {
            // It's an integer number of inches
            inches = atoi(size.c_str());
        }
        else
        {
            if (s > 0)
            {
                // Has an inch part and a fraction part
                inches = atoi(size.substr(0, s).c_str());
            }
            // Handle fractional part
            string fp = size.substr(s+1);
            if (fp.size() == 0)
            {
                cerr << size << " is not a proper size.\n";
                return;
            }
            if (fp.size() > 4)
            {
                cerr << size << " has more than 4 decimals.\n";
                return;
            }
            // Append zeros until we have 4 digits
            while (fp.size() < 4)
            {
                fp += "0";
            }
            fraction = atoi(fp.c_str());
        }
        target_value = inches*inches_to_tenths + fraction;
    }
 
 
    // Start constructing combinations and see if they sum to the
    // target value.
    const int n = n_sizes;
    int * combinations = new int(combination_limit + 1);
    int count = 0;
    cout << size;
    if (use_mm)
    {
        cout << " mm (";
        printf("%.4f inches)", double(target_value/1e4));
    } 
    cout << ":\n";
    for (int k = 1; k <= combination_limit; k++)
    {
        bool done = false;
        GetNextCombination(n, k, INIT, combinations);
        while (GetNextCombination(n, k, NoINIT, combinations) == NotDONE) 
        {
            if (TestArray(combinations, k, size, target_value))
            {
                done = true;
                break;
            }
            count++;
        }
        if (done)
            break;
    }

    if (show_number_combinations)
        cout << "  [" << count << " combinations checked]\n";
    cout << "\n";
    delete[] combinations;
}

void ShowBlockSizes(void)
{
    cout << "Block sizes used:\n";
    for (int i = 0; i < n_sizes; i++)
    {
        printf(" %7.4f\n", double(sizes[i])/inches_to_tenths);
    }
}

int main(int argc, char ** argv)
{
    program_name = argv[0];
    if (argc < 2)
    {
        Usage();
        return 1;
    }
    argv++;

    sizes = sizes_don;
    n_sizes = sizeof(sizes_don)/sizeof(int);

    while ((*argv)[0] == '-')
    {
        if ((*argv)[1] == '3' and (*argv)[2] == '6')   // -36
        {
            sizes = sizes_36;
            n_sizes = sizeof(sizes_36)/sizeof(int);
            argv++;
            continue;
        }

        if ((*argv)[1] == '8' and (*argv)[2] == '1')   // -81
        {
            sizes = sizes_81;
            n_sizes = sizeof(sizes_81)/sizeof(int);
            argv++;
            continue;
        }

        if ((*argv)[1] == 'a')   // -a
        {
            show_all = true;
            argv++;
            continue;
        }

        if ((*argv)[1] == 'k')   // -k
        {
            const string msg = "-k option requires an integer argument > 0\n";
            argv++;
            if (not *argv)
            {
                cerr << msg;
                return 1;
            }
            combination_limit = atoi(*argv);
            if (combination_limit <= 0)
            {
                cerr << msg;
                return 1;
            }
            argv++;
            if (not *argv)
            {
                Usage();
            }
            continue;
        }

        if ((*argv)[1] == 'm')   // -m
        {
            use_mm = true;
            argv++;
            continue;
        }

        if ((*argv)[1] == 'n')   // -n
        {
            show_number_combinations = true;
            argv++;
            continue;
        }

        if ((*argv)[1] == 's')   // -s
        {
            ShowBlockSizes();
            return 0;
        }

        if ((*argv)[1] == 'w')   // -w
        {
            wear_blocks = true;
            argv++;
            continue;
        }
        cerr << argv[0] << " is an unrecognized option." << endl;
        return 1;
    }
 
    CheckInput(argv);
    while (*argv)
    {
        ConstructBlockSet(string(*argv));
        argv++;
    }
}
