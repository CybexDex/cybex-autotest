## 测试用例脚本说明
该仓库测试用例脚本主要用于Cybex链的功能测试，可用Smoke测试、DailyBuilding、集成测试、系统测试等。

#### 1. 环境搭建
请先安装好python3和pip3
```Shell
pip3 install -U virtualenv 
python3 -m virtualenv venv 
source venv/bin/activate 
pip install pytest
```
拉最新的代码后
```Shell
cd autotestForCybex
pip install -r requirements.txt
```

#### 2.目录结构
目录结构解析：
```Shell
$ tree
.
├── README.md            // 使用说明
├── config.ini           // 用例配置文件，用来存放 链的连接方式/nathan账号等全局数据
├── conftest.py          // 存放fixture定义
├── docs                 // 用例文档文件夹
├── log                  // 运行日志文件夹
├── modules.py           // 工具方法库文件
├── pytest.ini           // pytest配置文件 
├── report               // 存放测试报告
├── requirements.txt     // 依赖库
├── test_account.py      // test_开头的文件为用例文件
├── test_asset.py        // test_开头的文件为用例文件
├── test_cybex_op.py     // test_开头的文件为用例文件
├── test_market.py       // test_开头的文件为用例文件
├── test_transfer.py     // test_开头的文件为用例文件
└── test_wallet.py       // test_开头的文件为用例文件
```
#### 3.执行用例

```Shell
cd autotestForCybex
pytest
```


```Shell
pytest --chain sarcychain    // 跑指定的链
pytest --timeout=0.5         // 设置超时时间
pytest --reruns 5 --reruns-delay 1        // 设置失败重跑，重跑次数为5次，每次重跑delay 1s
pytest -v -s test_account.py              // 跑指定的用例文件，展示详细信息
```

#### 4.加入新链
默认config.ini中配置了2条链，dextestchain和sarcychain，不指定链跑时默认使用dextestchain。如需要跑新的链，需要先将链相关的信息和nathan账号配置到config.ini文件中：

```Shell
[chainname]
node_url = ******
chain_id = ******
master_account = ******
master_pubkey = ******
master_privkey =  ******
```

举例：
```Shell
[sarcychain]
node_url = ws://47.75.211.121:28095
chain_id = c7b4ce772930412d54ba7b6ea31033c063f819cd16a83adf2c555981bad66f9a
master_account = nathan
master_pubkey = CYB6MRyAjQq8ud7hVNYcfnVPJqcVpscN5So8BhtHuGYqET5GDW5CV
master_privkey =  5KQwrPbwdL6PhXujxW37FSSQZ1JiwsST4cqQzDeyXtP79zkvFD3
```

#### 4.后续计划
持续更新，请关注。