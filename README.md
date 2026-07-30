## Dify 1.0 Plugin Database Query Tools


---


### Demonstration

Currently supported database types: mysql, oracle, [oracle11g](./db_query/README.md#2-how-to-connect-to-oracle-11g--如何连接oracle-11g), postgresql, mssql, Dameng (DM), or Apache Doris.

目前支持的数据库类型：mysql、oracle、[oracle11g](./db_query/README.md#2-how-to-connect-to-oracle-11g--如何连接oracle-11g)、postgresql、mssql、达梦（DM）、Apache Doris。

![db_query](db_query/_assets/db_query.png)

![db_query_sql_query](db_query/_assets/db_query_sql_query.png)

![db_query_chatflow](db_query/_assets/db_query_chatflow.png)


---



### Tools

#### Database Query Utils  数据库查询工具

![db_query](./images/db_query.png)



#### Database Query Utils (Pre-authorization)  数据库查询工具（预授权）

![db_query_pre_auth](./images/db_query_pre_auth.png)


---



### Installing Plugins via GitHub  通过 GitHub 安装插件

Can install the plugin using the GitHub repository address. Visit the Dify platform's plugin management page, choose to install via GitHub, enter the repository address, select version number and package file to complete installation.

可以通过 GitHub 仓库地址安装该插件。访问 Dify 平台的插件管理页，选择通过 GitHub 安装插件，输入仓库地址后，选择版本号和包文件完成安装。

![install_plugin_via_github](./images/install_plugin_via_github.png)



---


### Installing Plugins via Local 通过本地安装插件

If the plugin cannot be installed via GitHub due to network issues, you can [manually download plugin package](https://github.com/junjiem/dify-plugin-tools-dbquery/releases/latest).
Visit the Dify platform's plugin management page, choose Local Package File to complete installation.

如果由于网络问题导致无法通过 GitHub 安装插件，可以 [手动下载插件包](https://github.com/junjiem/dify-plugin-tools-dbquery/releases/latest)，访问 Dify 平台的插件管理页，选择通过本地插件完成安装。

![install_plugin_via_local](./images/install_plugin_via_local.png)



---



### FAQ

#### How to Handle Errors When Installing Plugins? 安装插件时遇到异常应如何处理？

**Issue**: If you encounter the error message: plugin verification has been enabled, and the plugin you want to install has a bad signature, how to handle the issue?

**Solution**: Add the following line to the end of your .env configuration file: FORCE_VERIFYING_SIGNATURE=false
Once this field is added, the Dify platform will allow the installation of all plugins that are not listed (and thus not verified) in the Dify Marketplace.

**问题描述**：安装插件时遇到异常信息：plugin verification has been enabled, and the plugin you want to install has a bad signature，应该如何处理？

**解决办法**：在 .env 配置文件的末尾添加 FORCE_VERIFYING_SIGNATURE=false 字段即可解决该问题。
添加该字段后，Dify 平台将允许安装所有未在 Dify Marketplace 上架（审核）的插件，可能存在安全隐患。



---



### Examples 示例

- [完蛋！我被LLM包围了！（Dify1.0战绩排行版）](./examples/完蛋！我被LLM包围了！（Dify1.0战绩排行版）.yml)

- [完蛋！我被LLM包围了！（Dify1.0战绩排行+留言版）](./examples/完蛋！我被LLM包围了！（Dify1.0战绩排行+留言版）.yml)


![](./db_query_pre_auth/_assets/llm_riddles1.png)

![](./db_query_pre_auth/_assets/llm_riddles2.png)

![](./db_query_pre_auth/_assets/llm_riddles3.png)



---



### Dify Plugin Downloading and Repackaging Scripting Tool  Dify插件下载并重打包脚本工具

Scripting tool for downloading Dify plugin package from Dify Marketplace and Github and repackaging [true] offline package (contains dependencies, no need to be connected to the Internet).

从Dify市场和Github下载Dify插件包并重新打【真】离线包（包含依赖，不需要再联网）的脚本工具。

Github Repo: https://github.com/junjiem/dify-plugin-repackaging



---



### Star history

[![Star History Chart](https://api.star-history.com/svg?repos=junjiem/dify-plugin-tools-dbquery&type=Date)](https://star-history.com/#junjiem/dify-plugin-tools-dbquery&Date)


