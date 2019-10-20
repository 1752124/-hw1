# -hw1
数据结构化存储及查询+多客户端查询

[1] 数据结构化存储和查询：10分 
1、给定文本文件（sample.txt）按照标点符号、空格、换行符等特殊分隔符提取单词（不计
数字），并对所提取单词按照alphabet进行排序（小写a-z, 然后A-Z），对每个单词转化
为字节数组byte[]。 2、依次将每个单词对应的字节数组byte[]拷贝到一个单位长度为1024的字节数组
byte[1024]，在进行copy的过程中，若copy第i个单词的字节数组byte[]超出byte[1024]范
围，那么当前字节数组byte[1024]则只保存截止第(i-1)个单词的字节数组byte[]，然后将
该字节数组byte[1024]写入文件（文件名为sort.dat）；然后重新初始化字节数组
byte[1024]，将第i个单词的字节数组byte[]拷贝到字节数组byte[1024]。示意图如下所示，
确保将单词的字节数组以固定长度1024的结构形式进行保存。
3、读取test.txt中的所有words，以random access方式访问sort.dat文件，查询test.txt中每
一个word在sort.dat中的下一个排序单词，并写到按行日志文件(out.log)中。
4、在以上步骤中，统计步骤2的存储时间和步骤3的查询时间，追加到out.log最后2行
测试要求：助教会给定10组sample.txt和test.txt文件，学生要求输出日志文件out.log，并画
曲线图，x轴为每组文件的编号，y轴为(存储/查询)时间.

[2] 多客户端查询：10分 
1、在服务器端启动Server Socket服务; 客户端通过Socket接口连接服务器, 将客户端本地
test.txt文件中words发送至服务器; 服务器获取客户端发送的words, 按照[1]作业的要
求将结果返回至客户端。
2、在满足上述功能的情况，通过多线程服务优化客户端获取访问结果的时间，具体如下，
设定服务器端启动m个线程(自1 – 5)、服务器端启动n个线程(自1 – 5)，计算客户端完成
获取结果的整体时间，要求画一个3维曲线图，x轴为m的值，y轴为n的值，z轴为时间。

Reference
1\ Random Access:
https://docs.oracle.com/javase/tutorial/essential/io/rafs.html
http://java.meritcampus.com/java-example-programs/288/Random-Access-File-Demo
http://ecomputernotes.com/java/stream/randomaccessfile
2\ Reading and writing binary files
http://www.javapractices.com/topic/TopicAction.do?Id=245
https://www.caveofprogramming.com/java/java-file-reading-and-writing-files-injava.html
3\Concurrency
https://docs.oracle.com/javase/tutorial/essential/concurrency/index.html
4\ Networking
https://docs.oracle.com/javase/tutorial/networking/index.html
