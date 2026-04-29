// arrays/AlphabeticSearch.java
// (c)2021 MindView LLC: see Copyright.txt
// We make no guarantees that this code is fit for any purpose.
// Visit http://OnJava8.com for more book information.
// Searching with a Comparator import
import java.util.*;
import onjava.*;
import static onjava.ArrayShow.*;

public class AlphabeticSearch {
  public static void main(String[] args) {
    // 生成一个包含30个随机字符串的数组，用于后续的排序和搜索演示
    String[] sa = new Rand.String().array(30);
    // 对字符串数组进行排序。
    // String.CASE_INSENSITIVE_ORDER 是一个比较器，它让排序时忽略字母的大小写（即 'A' 和 'a' 视为相同）。
    // 这样排序后的结果是按字母顺序排列，且不区分大写和小写。
    Arrays.sort(sa, String.CASE_INSENSITIVE_ORDER);
    show(sa);
    // 使用二分查找法在已排序的数组 sa 中查找元素 sa[10]。
    // 第一个参数：要搜索的数组（必须是已排序的）。
    // 第二个参数：要查找的目标键值（这里是数组中索引为10的元素）。
    // 第三个参数：比较器，必须与排序时使用的比较器一致（此处为忽略大小写的顺序）。
    // 如果找到元素，返回其索引；如果未找到，返回 -(插入点) - 1。
    int index = Arrays.binarySearch(sa,
      sa[10], String.CASE_INSENSITIVE_ORDER);
    System.out.println(
     "Index: "+ index + "\n"+ sa[index]);
  }
}
/* Output:
[anmkkyh, bhmupju, btpenpc, cjwzmmr, cuxszgv, eloztdv,
ewcippc, ezdeklu, fcjpthl, fqmlgsh, gmeinne, hyoubzl,
jbvlgwc, jlxpqds, ljlbynx, mvducuj, qgekgly, skddcat,
taprwxz, uybypgp, vjsszkn, vniyapk, vqqakbm, vwodhcf,
ydpulcq, ygpoalk, yskvett, zehpfmm, zofmmvm, zrxmclh]
Index: 10
gmeinne
*/
