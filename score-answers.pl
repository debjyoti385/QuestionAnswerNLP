#!/usr/bin/perl

# USAGE: perl score-answers.pl <response_file> <answerkey_file>
#


# **********************************************************************
#                         DATA STRUCTURES
# **********************************************************************

use Class::Struct; 

struct keyinfo => {
  qid => '$',
  question => '$',
  answer => '$',
  difficulty => '$',
}; 

struct respinfo => {
  qid => '$',
  answer => '$',
}; 


# **********************************************************************
#                MAIN FUNCTIONS & GLOBAL VARIABLES
# **********************************************************************

$recall_sum = 0;
$precision_sum = 0;
$fmeasure_sum = 0;
$num_questions = 0;
$num_questions_answered = 0;

$correctwords_sum = 0;
$respwords_sum = 0;
$keywords_sum = 0;

$num_args = @ARGV;
if ($num_args < 2) {
    print "ERROR: missing required input file.";
    print "Usage is: score-answer.pl <response_file> <answerkey_file>\n";
}
else {
    $response_file = $ARGV[0];
    $answerkey_file = $ARGV[1];
    my($keyinfo_list, $respinfo_list);  
    $keyinfo_list = read_anskey($answerkey_file);
    $respinfo_list = read_responses($response_file);
    $success = score($keyinfo_list, $respinfo_list);
    if ($success) {
	print_final_stats();
    }
    else {
	print "\n**************************************************\n\n";
	print "         ABORTING DUE TO MISALIGNMENT!";
	print "\n\n**************************************************\n";
    }
}


# ***********************************************************************
#                            FUNCTIONS
# ***********************************************************************


# Score all answers
sub score {
    my($keyinfo_list, $respinfo_list) = @_;

    while (($keyinfo = shift(@$keyinfo_list)) &&
	   ($respinfo = shift(@$respinfo_list))) {
	$qid = $keyinfo->qid;

	# Make sure QIDs are the same
	if ($respinfo->qid !~ /^$qid$/i) {
	    print "ERROR: Key and Response not aligned properly!!!\n";
	    print "Key QID = $qid    Respond QID = "; 
	    print $respinfo->qid;  print "\n";
	    return(0);   # return failure
	}
	else {
	    score_info($keyinfo, $respinfo);
	}
    }
    return(1);  # return success
}


# Score one particular answer
sub score_info {
    my($keyinfo, $respinfo) = @_;
    my($qid, $keyans, $respans, @keyoptions, $option);
    my($recall,$precision,$fmeasure,$correct,$numkeywords,$numrespwords);
    my($best_recall, $best_precision, $best_correct, $best_keywords);
    my($best_numrespwords, $best_keymatch, $num_options);
    my($best_fmeasure) = -1;
    
    $qid = $keyinfo->qid;
    print "-----------------------------------------------------------------------------------------\n";
    print "\nSCORING $qid\n";
    $keyans = $keyinfo->answer;
    $respans = $respinfo->answer;
    @keyoptions = split /\s*\|\s*/, $keyans;
    $num_options = @keyoptions;
    foreach $option (@keyoptions) {
	($recall,$precision,$fmeasure,$correct,$numkeywords,$numrespwords) 
	    = score_strings($option, $respans);
	if ((($fmeasure =~ /^-$/) && ($best_fmeasure == -1)) ||
	    ($fmeasure > $best_fmeasure)) {
	    $best_keymatch = $option;
	    $best_recall = $recall;
	    $best_precision = $precision;
	    $best_fmeasure = $fmeasure;
	    $best_correct = $correct;
	    $best_keywords = $numkeywords;
	    $best_numrespwords = $numrespwords;
	}
    }

    $recall_sum += $best_recall;
    $precision_sum += $best_precision;
    $fmeasure_sum += $best_fmeasure;
    $num_questions++;
    if ($best_numrespwords > 0) {  # don't increment if no response words!
	$num_questions_answered++;
    }

    $correctwords_sum += $best_correct;
    $respwords_sum += $best_numrespwords;
    $keywords_sum += $best_keywords;

    if ($num_options > 1) {
	print "\n=> Best match in answer key is:\n   `$best_keymatch'\n";
    }
    print_stats($best_recall, $best_precision, $best_fmeasure, 
		$best_correct, $best_keywords, $best_numrespwords);
}


# String matching procedure
sub score_strings {
    my($keystr, $respstr) = @_;
    my(@keywords) = (); my(@respwords) = ();
    my($correct) = 0; my($spurious) = 0; my($missed) = 0; 
    my($numkeywords, $numrespwords, $fmeasure, $recall, $precision);

    print "\nComparing Key  `$keystr'\n      and Resp `$respstr'\n";
    @keywords = split /\s+/, $keystr;
    @respwords = split /\s+/, $respstr;

    strip_punctuation(\@keywords);
    strip_punctuation(\@respwords);

    $numkeywords = @keywords;
    $numrespwords = @respwords;
    foreach $respword (@respwords) {
	if (member($respword, @keywords)) {
	    # print "Found `$respword' in `@keywords'\n";
	    $correct++;
	    @keywords = remove($respword, @keywords);
	}
	else {
	    $spurious++;
	}
    }
    $missed = @keywords;  # number of unmatched words left in @keywords
 
    ($recall, $precision, $fmeasure) = 
	compute_stats($correct, $numkeywords, $numrespwords);

    return($recall, $precision, $fmeasure, $correct, $numkeywords,
	   $numrespwords);
} 


sub strip_punctuation {
    my($words) = @_;
    my($num_words, $word);

    $num_words = @$words;
    # strip off leading and trailing punctuation
    # (punctuation in the middle of a word is fine! Consider things like
    # decimal points in numbers, apostrophes, etc.)
    #
    for ($i=0; $i < $num_words; $i++) {
	@$words[$i] =~ s/^[,:;\.\!\?\'\"\(\{\)\}]//;   
	@$words[$i] =~ s/[,:;\.\!\?\'\"\(\{\)\}]$//;   
    }

    # check for words that are the empty string (meaning that they
    # consisted of ONLY punctutation symbols before the strippage above)
    # and remove them from the list of words
    for ($i=0; $i < $num_words; $i++) {
	$word = shift(@$words);
	if ($word !~ /^$/) {  # not empty string so push back on
	    push(@$words, $word);
	}
    }
}


# computes recall, precision, and fmeasure
sub compute_stats {
    my($correct, $numkeywords, $numrespwords) = @_;
    my($recall, $precision, $fmeasure);

    if ($numkeywords > 0) {
	$recall = $correct / $numkeywords;
    }
    else {
	$recall = "-";
    }
    if ($numrespwords > 0) {
	$precision = $correct / $numrespwords;
    }
    else {
	$precision = "-";
    }
    $fmeasure = compute_fmeasure($recall, $precision);
    return($recall, $precision, $fmeasure);
}

sub compute_fmeasure {
    my($recall, $precision) = @_;
    my($f, $denom);

    if (($recall =~ /^-$/) || ($precision =~ /^-$/)) {
	return("-");
    }
    else {
	$denom = $recall + $precision;
	if ($denom > 0) {
	    $f = (2 * $recall * $precision) / $denom;
	}
	else {
	    $f = 0;
	}
	return($f);
    }
}

sub member {
    my($target, @lst) = @_;
    my($found) = 0;
    my($item);

    while (!$found && (@lst)) {
	$item = shift @lst;
	if ($item =~ /^\Q$target\E$/i) {
	    $found = 1;
	}
    }
    return ($found);
}

sub remove {
    my($target, @lst) = @_;
    my($found) = 0;
    my($item);
    my(@newlst) = ();

#    print "Removing `$target'\n";
#    print "Initial list = @lst\n";
    while ($item = shift @lst) {
	if ($found || ($item !~ /^$target$/i)) {  # retain everything except the  
	    push(@newlst, $item);       # *first* string that matches. All other  
	}                               # instances should be retained.
	else { 
	    $found = 1;
	} 
    }
#    print "Modified list = @newlst\n";
    return(@newlst);
}
    


# Reads in an answer key file
sub read_anskey {
    my($file) = @_;
    my($qid, $question, $answer, $difficulty, $keyinfo);
    my(@keyinfo_list) = ();

    open(INPUT_STREAM, "$file") || die "ERROR: Couldn't open file $file\n";
    while ($line = <INPUT_STREAM>) {
	if ($line =~ /^\s+$/) {  # skip blank lines between questions
	    next;
	}
	if ($line =~ /^QuestionID:\s*(.*?)\s*$/i) {
	    $qid = $1;
	}
	else {
	    print "ERROR: Expected Question ID but found: $line\n";
	}
	$line = <INPUT_STREAM>;
	if ($line =~ /^Question:\s*(.*?)\s*$/i) {
	    $question = $1;
	}
	else {
	    print "ERROR: Expected Question but found: $line\n";
	}
	$line = <INPUT_STREAM>;
	if ($line =~ /^Answer:\s*(.*?)\s*$/i) {
	    $answer = $1;
	}
	else {
	    print "ERROR: Expected Answer but found: $line\n";
	}
	$line = <INPUT_STREAM>;
	if ($line =~ /^Difficulty:\s*(.*?)\s*$/i) {
	    $difficulty = $1;
	}
	else {
	    print "ERROR: Expected Difficulty but found: $line\n";
	}
	$keyinfo = create_keyinfo($qid, $question, $answer, $difficulty);
	push(@keyinfo_list, $keyinfo);
    }
    return(\@keyinfo_list);
}
    
# Reads in a system-generated response file
sub read_responses {
    my($file) = @_;
    my($qid, $answer, $respinfo);
    my(@respinfo_list) = ();

    open(INPUT_STREAM, "$file") || die "ERROR: Couldn't open file $file\n";
    while ($line = <INPUT_STREAM>) {
	if ($line =~ /^\s+$/) {  # skip blank lines between questions
	    next;
	}
	if ($line =~ /^QuestionID:\s*(.*?)\s*$/i) {
	    $qid = $1;
	}
	else {
	    print "ERROR: Expected QuestionID but found: $line\n";
	}
	$line = <INPUT_STREAM>;
	if ($line =~ /^Answer:\s*(.*?)\s*$/i) {
	    $answer = $1;
	}
	else {
	    print "ERROR: Expected Answer but found: $line\n";
	}
	$respinfo = create_respinfo($qid, $answer);
	push(@respinfo_list, $respinfo);
    }
    return(\@respinfo_list);
}

sub create_keyinfo {
    my($qid, $question, $answer, $difficulty) = @_;
    my($keyinfo);

    $keyinfo = keyinfo->new();
    $keyinfo->qid($qid);
    $keyinfo->question($question);
    $keyinfo->answer($answer);
    $keyinfo->difficulty($difficulty);
    return($keyinfo);
}

sub print_keyinfo {
    my($keyinfo) = @_;
    my($qid, $question, $answer, $difficulty);

    $qid = $keyinfo->qid;
    $question = $keyinfo->question;
    $answer = $keyinfo->answer;
    $difficulty = $keyinfo->difficulty;
    print "QUESTION ID: `$qid'\n";
    print "QUESTION   : `$question'\n";
    print "ANSWER     : `$answer'\n";
    print "DIFFICULTY : `$difficulty'\n\n";
}

sub create_respinfo {
    my($qid, $answer) = @_;
    my($respinfo);

    $respinfo = respinfo->new();
    $respinfo->qid($qid);
    $respinfo->answer($answer);
    return($respinfo);
}

sub print_respinfo {
    my($respinfo) = @_;
    my($qid, $answer);

    $qid = $respinfo->qid;
    $answer = $respinfo->answer;
    print "QUESTION ID: `$qid'\n";
    print "ANSWER     : `$answer'\n\n";
}

# Given a string and number N, this function pads spaces onto the right
# side of the string until the string has length N.
#
sub pad_w_spaces {
    my($str,$N) = @_;

    my($len) = length $str;
    while ($len < $N) {
        $str = $str . " ";
        $len = length $str;
    }
    return($str);
}

sub print_stats {
    my($recall, $precision, $fmeasure, $correct, $numkeywords, $numrespwords) = @_;

    print "\nRecall    = "; 
    if ($recall !~ /^-$/) {
	printf "%.2f", $recall;
    }
    else {
	print "N/A";
    }
    print " ($correct/$numkeywords)\n";
    
    print "Precision = "; 
    if ($precision !~ /^-$/) {
	printf "%.2f", $precision; 
    }
    else {
	print "N/A";
    }
    print " ($correct/$numrespwords)\n";

    print "F-measure = "; 
    if ($fmeasure !~ /^-$/) {
	printf "%.2f", $fmeasure;
    }
    else  {
	print "N/A";
    }
    print "\n\n";
}


sub print_final_stats {
    my($avg_recall, $avg_precision, $avg_fmeasure);
    my($overall_recall, $overall_precision, $overall_fmeasure);

    print "\n\nFinished processing $num_questions questions, ";
    print "$num_questions_answered of which had responses.\n";
    print "*************************************************************************\n\n";
    print "FINAL RESULTS\n\n";

    # These are word-based version of R, P, and F
#    ($overall_recall, $overall_precision, $overall_fmeasure) = 
#	compute_stats($correctwords_sum, $keywords_sum, $respwords_sum);
#    print_stats($overall_recall, $overall_precision, 
#      $overall_fmeasure, $correctwords_sum, $keywords_sum,$respwords_sum);

    if ($num_questions > 0) {
	$avg_recall = $recall_sum / $num_questions;
	if ($num_questions_answered > 0) {
	    $avg_precision = $precision_sum / $num_questions_answered;
	}
	else {  # System didn't produce ANY answers if we get here! 
	    $avg_precision = 0;
	}
	$avg_fmeasure = compute_fmeasure($avg_recall, $avg_precision);
	
	print "AVERAGE RECALL =    "; printf "%.4f", $avg_recall; 
	print "  ("; printf "%.2f", $recall_sum; 
	print " / $num_questions)";
	print "\nAVERAGE PRECISION = "; printf "%.4f", $avg_precision; 
	print "  ("; printf "%.2f", $precision_sum; 
	print " / $num_questions_answered)";
	print "\nAVERAGE F-MEASURE = "; printf "%.4f", $avg_fmeasure; 
	print "\n\n";
	print "*************************************************************************\n";
    }
    else {
	print "ERROR: No questions/answers found!\n";
    }
}

