## 这里有两个版本的服务器，最早的版本是双线程来实现的，因为socket.recv()阻塞的缘故。210816的版本是用python IO多路复用写的新版本。和文档里面selectors模块的例子很像。但我加了详细的个人理解注释在里面。非常详细了。当然也需要对原版本的服务器代码做些修改。 
## 这个代码再第三次开发拓展的方向，可以把服务器注册用的addr数量从一个给拓展到本地域名下的多个。再给当前的选择器加一层。
