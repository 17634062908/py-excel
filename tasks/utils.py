# -*- coding: utf-8 -*-
import sys
try:
    reload(sys)
    sys.setdefaultencoding('utf-8')
except:
    print 'set default encoding error'

class Utils:

    WORD_CATE_PORN = 1  # 色情
    WORD_CATE_POLITICAL = 2  # 政治
    WORD_CATE_SOCIAL = 3  # 社会
    WORD_CATE_GAMBLE = 4  # 赌博
    WORD_CATE_TERROR = 5  # 暴恐
    WORD_CATE_REACTION = 6  # 反动
    WORD_CATE_DRUG = 7  # 毒品
    WORD_CATE_OTHER = 9  # 其他

    WORD_LEVEL_TRACE = 1    # 跟踪
    WORD_LEVEL_INFO = 3     # 突出
    WORD_LEVEL_WARN = 5     # 警告
    WORD_LEVEL_ERROR = 7    # 危险
    WORD_LEVEL_FATAL = 9    #致命

    STATUS_NOTSET = 1
    STATUS_DEALING = 5
    STATUS_ERROR = 10
    STATUS_SUCCESS = 20

    @classmethod
    def get_keyword_cates(cls, key=False):
        cates = {
            u'色情': Utils.WORD_CATE_PORN,
            u'政治': Utils.WORD_CATE_POLITICAL,
            u'社会': Utils.WORD_CATE_SOCIAL,
            u'赌博': Utils.WORD_CATE_GAMBLE,
            u'暴恐': Utils.WORD_CATE_TERROR,
            u'反动': Utils.WORD_CATE_REACTION,
            u'毒品': Utils.WORD_CATE_DRUG,
            u'其他': Utils.WORD_CATE_OTHER,
        }
        if key is False:
            return cates
        return cates.get(key, False)

    @classmethod
    def get_keyword_levels(cls, category=False):
        levels = {
            u'跟踪': Utils.WORD_LEVEL_TRACE,
            u'突出': Utils.WORD_LEVEL_INFO,
            u'警告': Utils.WORD_LEVEL_WARN,
            u'危险': Utils.WORD_LEVEL_ERROR,
            u'致命': Utils.WORD_LEVEL_FATAL
        }
        if category is False:
            return levels
        return levels.get(category, False)