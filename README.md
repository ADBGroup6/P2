# Information-Extraction-System
## COMS E6111 Advanced Database System - Project 2 
### a) Project 2 Group6
  Wanheng Li (wl2573)    
  Yibo Xu (yx2387)
### b) List of Files    
main.py   
data.py    
NLPCore.py     
PythonNLPCore      
stanford-corenlp-full-2017-06-09
### c) Instruction for Running the Program
**Installation:**            
pip install beautifulsoup4     
sudo apt-get update wget http://nlp.stanford.edu/software/stanford-corenlp-full-2017-06-09.zip   
sudo apt-get install unzip     
unzip stanford-corenlp-full-2017-06-09.zip    
sudo apt-get install default-jdk       
git clone https://github.com/infobiac/PythonNLPCore.git  

**Command:**    
Please run the program with following commond:    
[Directory] [Google API Key] [Google Engine ID] [r] [t] [q] [k] .        
**r** is an integer between 1 and 4 as relation to extract.    
**t** is a real number between 0 and 1 as minimum extraction confidence.    
**q** is a list of words as "seed query".    
**k** is an integer greater than 0 as number of tuples required.     
e.g. python main.py AIzaSyAPbX4JVlc8waFre4Zve1v8zx1VSfhijIk 008083549322187859573:yubw3z65huy 4 0.35 "bill gates microsoft" 10
### d) Internal Design        
1. Input the relation **r** to extract (1.Live_In 2.Located_In 3.OrgBased_In 4.Work_For), extraction confidence threshold **t**, a list of workds as "seed query" **q**, and number of tuples required **k**. The program will present all these inputs, including relevant key info as well.        
2. The program calls Google Custom Search API to retrieve top-10 URLs with current query words, which will be used for iterative set expansion (ISE) later.        
3. For each unprocessed URL, extract the actual plain text from the webpage. Annotate the text with Stanford CoreNLP software suite, in particular, with Stanford Relation Extractor with specified input parameter **r**. The details for this step will be discussed in part **e**. Only the instances with r as the highest extraction confidence are considered. 
4. Terminate the programm if calculated precision is equal or larger than target value, which means the desired precision reached. The program will also terminate given no relevant results, which means the query can no longer be augmented.      
4. Identify the tuples with extraction confidence of at least t and add them to set **X**. Remove exact duplicates from set X and keep the only copy with the highest extraction confidence.
5. If set **X** already contains at least k tuples, return top-k such tuples sorted in decreasing order by extraction confidence and corresponding extraction confidence, and stop. Otherwise, go to next iteration and use the unseen tuple y with highest extraction confidence for next query. If there is no such tuple y, terminate the program before retrieving k high-confidence tuples.
### e) Performing Annotation and Information Extraction        
1. Run Stanford CoreNLP and Relation Extractor software to annotate the plain text from webpage and extract tuples for target relation r. Since the **parse** annotator is computationally expensive, we implement two pipelines to minimized the usage of it.     
2. For first pipeline, identify the sentences from the webpage text together with named entities for full text extracted from the webpage. Identify the with sepecifed relation to extract.         
3. For second pipeline, the RelationExtractorAnnotator predicts out of the four relations type for each sentence, which are Live_In, Located_In, OrgBased_In, Work_For and _NR. If the relation type with the highest extraction confidence is identical to that of input relation parameter **r**, this tuple will be considered for extraction tuples set.
### f) Relevant Key
**Google Custom Search Engine API Key:**      
AIzaSyAPbX4JVlc8waFre4Zve1v8zx1VSfhijIk       
        
**Engine ID:**        
008083549322187859573:yubw3z65huy
### g) Additional Information        
1. Please make sure the path for 'stanford-corenlp-full-2017-06-09' is correct to run the program.

