package com.JavaWithPython;

/*
 * @Descripttion: 
 * @Version: xxx
 * @Author: WanJu
 * @Date: 2021-05-24 20:33:55
 * @LastEditors: WanJu
 * @LastEditTime: 2021-05-26 11:52:56
 */
import java.io.File;
import com.alibaba.fastjson.JSONObject;

public class DiskPredict {
    private final static String root_path = "\"E:\\BackBlaze\\DP_test\"";

    public static void DataPreProcess(String filePath, int replace){
        // 需要检查参数正确性
        System.out.println("[JAVA--> ] DataPreProcess:");
        JSONObject param = new JSONObject();
        param.put("\"file_path\"", filePath);
        param.put("\"replace\"", replace);
        param.put("\"root_path\"", root_path);
        JavaExePython.execPython("python" + File.separator + "preprocess.py", param);
        System.out.println("[JAVA--> ] Complete.\n");
    }

    public static void GetTrainData(String filePath, float scale, float verifySize){
        // 需要检查参数正确性
        System.out.println("[JAVA--> ] GetTrainData:");
        JSONObject param = new JSONObject();
        param.put("\"file_path\"", filePath);
        param.put("\"scale\"", scale);
        param.put("\"verifySize\"", verifySize);
        param.put("\"root_path\"", root_path);
        JavaExePython.execPython("python" + File.separator + "get_data.py", param);
        System.out.println("[JAVA--> ] Complete.\n");
    }


    public static void Train(String filePath, String model, JSONObject params){
        // 需要检查参数正确性
        System.out.println("[JAVA--> ] Train:");
        JSONObject param = new JSONObject();
        param.put("\"file_path\"", filePath);
        param.put("\"model\"", model);
        param.put("\"params\"", params.toJSONString());
        param.put("\"root_path\"", root_path);
        JavaExePython.execPython("python" + File.separator + "traditional.py", param);
        System.out.println("[JAVA--> ] Complete.\n");
    }

    public static void Predict(String filePath){
        // 需要检查参数正确性
        System.out.println("[JAVA--> ] Predict:");
        JSONObject param = new JSONObject();
        param.put("\"file_path\"", filePath);
        param.put("\"root_path\"", root_path);
        JavaExePython.execPython("python" + File.separator + "disk_predict.py", param);
        System.out.println("[JAVA--> ] Complete.\n");
    }
}
