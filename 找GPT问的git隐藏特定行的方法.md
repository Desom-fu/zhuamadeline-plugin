
1. 配置 Git 过滤器
运行以下命令，创建一个合并的过滤规则：

bash
复制
编辑
git config filter.hide_sensitive.smudge "cat"
解释
在 Git 版本库中，commit 和 push 后，代码会变成：

python
复制
编辑

4. 让 Git 重新索引所有文件
Git 需要重新索引，才能应用 .gitattributes 变化：

bash
复制
编辑
git rm --cached -r .
git add .
git commit -m "Apply Git filter to hide sensitive lines and blocks"
git push origin main
5. 取消过滤（如果以后不想隐藏）
如果你不想再隐藏内容，可以运行：

bash
复制
编辑
git config --unset filter.hide_sensitive.clean
git config --unset filter.hide_sensitive.smudge
然后删除 .gitattributes 里的 * filter=hide_sensitive 规则。

最终效果
