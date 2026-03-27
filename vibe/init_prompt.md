请帮我写一个本地机密文档翻译系统，要求如下：
- 功能完全离线。
- 包含ui界面（可以是网页），使用现代简介的ui风格，例如毛玻璃，圆角等。可以选择深色模式和浅色模式。默认使用浅色模式。
- 可以选择本地大模型（如qwen），根据机器情况选择合适的大小并让用户确认，用户可以选择确认。
- 可以翻译用户给定的文字，同时，可以读取图片，PDF，md，xlsx，csv等常见格式，并翻译（如果能把翻译内容导出到对应的文件格式最好）。
- 支持多语种翻译，可以自动判断翻译语言，要求对中文，英语，德语，法语的翻译要有好的支持
- 可以根据机器语言自动设置gui的语言，也可以由用户选择
- 项目的开发语言使用python，ui使用vue，使用现代开发工具和框架，不要过于简化或复杂
- 要包含测试代码。并使用swagger和storybook来管理和展示动态测试用例。
- 本项目包含GitHub Actions CICD，可以自动构建，测试，部署。
- 包含Linux (ubuntu), windows, macos的安装包，并且这些安装包可以通过GitHub release自动发布。
- 项目使用MIT协议开源。
- 包含详细的开发文档和使用文档，包含英文和中文。使用文档使用mkdocs发布到GitHub pages。注意不要使用默认的mkdocs主题，使用贴近现代产品的主页+文档风格。要包含示例演示。
- 给项目起一个好听易懂吸引人的名字，并设计一个logo。
- 生成中英文的README.md文件。要给出所有有必要的badges, 包含但不限于在线文档链接等。
- 所有内容完成后自动format，test，随后commit并push到GitHub。监听actions的运行结果，直到actions成功运行。如果actions失败，则修复错误并重新开始。
- Building of the system should following the coding principles as in skills like ui-ux-pro-max-skill
 (https://github.com/nextlevelbuilder/ui-ux-pro-max-skill/tree/main), superpowers
(https://github.com/obra/superpowers/tree/main), Agent-Skills-for-Context-Engineering
 (https://github.com/muratcankoylan/Agent-Skills-for-Context-Engineering), etc. You can download these skills if needed. You can also check the following repositories for more useful skills:
 - https://skills.sh/
 - https://github.com/vercel-labs/skills
 - https://github.com/ComposioHQ/awesome-claude-skills
 Research them carefully. If you can not access some of them due to the login requirement, try to use the search engine to find the source code or some screenshots to understand their design and features.
- 对于以上内容进行深度分析，修正错误和不足之处，补充缺失部分，并输出一个详细的开发计划，然后执行开发计划。