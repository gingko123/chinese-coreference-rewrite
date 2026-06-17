import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"

MALE_NAMES = ["小明", "小刚", "小强", "小华", "小李", "张伟", "王强", "陈明", "刘洋", "吴磊"]
FEMALE_NAMES = ["小红", "小丽", "小芳", "小美", "小雅", "李娜", "王芳", "杨静", "周敏", "赵婷"]
OBJECTS = ["书", "作业", "礼物", "手机", "产品", "系统", "项目", "文章", "报告", "电脑", "钥匙", "论文", "政策", "方案", "课程", "活动", "会议", "订单"]
ORGS = [
    ("华为公司", "该公司"),
    ("腾讯公司", "该公司"),
    ("百度公司", "该公司"),
    ("清华大学", "该校"),
    ("复旦大学", "该校"),
    ("北京大学", "该校"),
    ("研究团队", "该团队"),
    ("某企业", "该企业"),
]


def sample(text, pairs, rewrite):
    return {
        "text": text,
        "coreference": [{"pronoun": p, "antecedent": a} for p, a in pairs],
        "rewrite": rewrite,
    }


def person_object_samples():
    rows = []
    names = [(name, "他") for name in MALE_NAMES] + [(name, "她") for name in FEMALE_NAMES]
    verbs = ["整理", "完成", "检查", "保存", "阅读", "修改"]
    for idx, (name, pronoun) in enumerate(names * 2):
        obj = OBJECTS[idx % len(OBJECTS)]
        verb = verbs[idx % len(verbs)]
        text = f"{name}{verb}了{obj}，{pronoun}准备再次确认它。"
        rewrite = f"{name}{verb}了{obj}，{name}准备再次确认{obj}。"
        rows.append(sample(text, [(pronoun, name), ("它", obj)], rewrite))
    return rows[:40]


def transfer_samples():
    rows = []
    objects = ["报告", "文章", "论文", "作业", "电脑", "手机", "钥匙", "礼物", "书", "方案"]
    pairs = list(zip(MALE_NAMES, FEMALE_NAMES)) + list(zip(FEMALE_NAMES, MALE_NAMES))
    for idx, (sender, receiver) in enumerate(pairs + pairs[:5]):
        obj = objects[idx % len(objects)]
        pronoun = "她" if receiver in FEMALE_NAMES else "他"
        action = "阅读" if obj in {"报告", "文章", "论文", "书", "方案"} else "检查"
        text = f"{sender}把{obj}交给{receiver}，{pronoun}认真{action}了它。"
        rewrite = f"{sender}把{obj}交给{receiver}，{receiver}认真{action}了{obj}。"
        rows.append(sample(text, [(pronoun, receiver), ("它", obj)], rewrite))
    return rows[:25]


def org_samples():
    rows = []
    objects = ["产品", "系统", "报告", "平台", "政策", "方案", "课程", "活动"]
    for idx in range(25):
        org, org_pronoun = ORGS[idx % len(ORGS)]
        obj = objects[idx % len(objects)]
        text = f"{org}发布了新{obj}，{org_pronoun}表示它将在下个月正式使用。"
        rewrite = f"{org}发布了新{obj}，{org}表示{obj}将在下个月正式使用。"
        rows.append(sample(text, [(org_pronoun, org), ("它", obj)], rewrite))
    return rows


def deictic_object_samples():
    rows = []
    templates = [
        ("学校购买了系统，该系统用于课程管理。", "该系统", "系统", "学校购买了系统，系统用于课程管理。"),
        ("团队撰写了报告，该报告总结了实验结果。", "该报告", "报告", "团队撰写了报告，报告总结了实验结果。"),
        ("平台上线了产品，该产品吸引了很多用户。", "该产品", "产品", "平台上线了产品，产品吸引了很多用户。"),
        ("政府发布了通知，该通知要求企业及时申报。", "该通知", "通知", "政府发布了通知，通知要求企业及时申报。"),
        ("公司开发了项目，这个项目已经进入测试阶段。", "这个项目", "项目", "公司开发了项目，项目已经进入测试阶段。"),
        ("研究团队提出了方案，该方案提升了系统响应速度。", "该方案", "方案", "研究团队提出了方案，方案提升了系统响应速度。"),
        ("学校开设了课程，该课程要求学生完成项目。", "该课程", "课程", "学校开设了课程，课程要求学生完成项目。"),
        ("学院举办了活动，该活动吸引了很多学生参加。", "该活动", "活动", "学院举办了活动，活动吸引了很多学生参加。"),
        ("医院召开了会议，该会议讨论了预约系统升级问题。", "该会议", "会议", "医院召开了会议，会议讨论了预约系统升级问题。"),
        ("平台收到了一笔订单，该订单将在明天完成配送。", "该订单", "订单", "平台收到了一笔订单，订单将在明天完成配送。"),
    ]
    for text, pronoun, antecedent, rewrite in templates * 3:
        rows.append(sample(text, [(pronoun, antecedent)], rewrite))
    return rows[:30]


def real_corpus_samples():
    easy = [
        sample("教育部发布了新政策，该政策将支持高校建设人工智能课程。", [("该政策", "政策")], "教育部发布了新政策，政策将支持高校建设人工智能课程。"),
        sample("某企业上线了智能客服系统，该企业表示它可以减少人工成本。", [("该企业", "某企业"), ("它", "系统")], "某企业上线了智能客服系统，某企业表示系统可以减少人工成本。"),
        sample("学校开设了自然语言处理课程，该课程要求学生完成项目。", [("该课程", "课程")], "学校开设了自然语言处理课程，课程要求学生完成项目。"),
        sample("平台收到了一笔订单，该订单将在明天完成配送。", [("该订单", "订单")], "平台收到了一笔订单，订单将在明天完成配送。"),
        sample("研究团队提出了优化方案，该方案提升了系统响应速度。", [("该方案", "方案")], "研究团队提出了优化方案，方案提升了系统响应速度。"),
        sample("医院召开了线上会议，该会议讨论了预约系统升级问题。", [("该会议", "会议")], "医院召开了线上会议，会议讨论了预约系统升级问题。"),
        sample("学院举办了学术活动，该活动吸引了很多学生参加。", [("该活动", "活动")], "学院举办了学术活动，活动吸引了很多学生参加。"),
        sample("李娜采访了张伟，她认为他提出的方案很有价值。", [("她", "李娜"), ("他", "张伟")], "李娜采访了张伟，李娜认为张伟提出的方案很有价值。"),
        sample("王强把报告发给王芳，她修改了它。", [("她", "王芳"), ("它", "报告")], "王强把报告发给王芳，王芳修改了报告。"),
        sample("清华大学更新了课程平台，该校表示它将服务更多学生。", [("该校", "清华大学"), ("它", "平台")], "清华大学更新了课程平台，清华大学表示平台将服务更多学生。"),
    ]
    generated = []
    scenarios = [
        ("银行推出了金融产品，该产品面向年轻用户。", "该产品", "产品", "银行推出了金融产品，产品面向年轻用户。"),
        ("政府发布了扶持政策，该政策覆盖中小企业。", "该政策", "政策", "政府发布了扶持政策，政策覆盖中小企业。"),
        ("医院升级了预约系统，该系统缩短了排队时间。", "该系统", "系统", "医院升级了预约系统，系统缩短了排队时间。"),
        ("学校公布了课程通知，该通知提醒学生按时选课。", "该通知", "通知", "学校公布了课程通知，通知提醒学生按时选课。"),
        ("研究团队完成了实验报告，该报告记录了模型结果。", "该报告", "报告", "研究团队完成了实验报告，报告记录了模型结果。"),
        ("某企业启动了研发项目，该项目计划持续三个月。", "该项目", "项目", "某企业启动了研发项目，项目计划持续三个月。"),
        ("平台优化了推荐方案，该方案提高了用户点击率。", "该方案", "方案", "平台优化了推荐方案，方案提高了用户点击率。"),
        ("学院组织了分享会议，该会议介绍了课程项目经验。", "该会议", "会议", "学院组织了分享会议，会议介绍了课程项目经验。"),
        ("学校举办了竞赛活动，该活动鼓励学生组队参赛。", "该活动", "活动", "学校举办了竞赛活动，活动鼓励学生组队参赛。"),
        ("平台处理了一笔订单，该订单因为地址错误被延迟。", "该订单", "订单", "平台处理了一笔订单，订单因为地址错误被延迟。"),
    ]
    for text, pronoun, antecedent, rewrite in scenarios * 3:
        generated.append(sample(text, [(pronoun, antecedent)], rewrite))

    hard = [
        sample("上海市启动了城市更新计划，该城市希望它改善居民生活环境。", [("该城市", "上海市"), ("它", "计划")], "上海市启动了城市更新计划，上海市希望计划改善居民生活环境。"),
        sample("小明告诉小刚，他已经完成了作业。", [("他", "小刚")], "小明告诉小刚，小刚已经完成了作业。"),
        sample("王芳采访了李娜，她提到这项活动很有意义。", [("她", "李娜"), ("这项活动", "活动")], "王芳采访了李娜，李娜提到活动很有意义。"),
    ]
    return (easy + generated[:27] + hard)[:40]


def write_json(name, rows):
    path = DATA_DIR / f"{name}.json"
    path.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main():
    constructed = (
        person_object_samples()
        + transfer_samples()
        + org_samples()
        + deictic_object_samples()
    )
    constructed = constructed[:120]
    demo = constructed[:10]
    dev = constructed[10:60]
    test = constructed[60:120]
    real = real_corpus_samples()

    write_json("samples", constructed)
    write_json("demo", demo)
    write_json("dev", dev)
    write_json("test", test)
    write_json("real_corpus", real)

    print(
        {
            "samples": len(constructed),
            "demo": len(demo),
            "dev": len(dev),
            "test": len(test),
            "real_corpus": len(real),
        }
    )


if __name__ == "__main__":
    main()
