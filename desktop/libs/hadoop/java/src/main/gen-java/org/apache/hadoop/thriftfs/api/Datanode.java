/**
 * Autogenerated by Thrift Compiler (0.7.0)
 *
 * DO NOT EDIT UNLESS YOU ARE SURE THAT YOU KNOW WHAT YOU ARE DOING
 */
package org.apache.hadoop.thriftfs.api;

import java.util.List;
import java.util.ArrayList;
import java.util.Map;
import java.util.HashMap;
import java.util.EnumMap;
import java.util.Set;
import java.util.HashSet;
import java.util.EnumSet;
import java.util.Collections;
import java.util.BitSet;
import java.nio.ByteBuffer;
import java.util.Arrays;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class Datanode {

  /**
   * Provides an interface to data nodes, so that clients may read and write
   * data blocks.
   */
  public interface Iface {

    /**
     * Read bytes from a block.
     * 
     * Only 2^31 - 1 bytes may be read on a single call to this method.
     * 
     * @param ctx
     * @param block Block to be read from.
     * 
     * @param offset Offset within the block where read must start from.
     * 
     * @param length Number of bytes to read.
     */
    public BlockData readBlock(org.apache.hadoop.thriftfs.api.RequestContext ctx, Block block, long offset, int length) throws org.apache.hadoop.thriftfs.api.IOException, org.apache.thrift.TException;

  }

  public interface AsyncIface {

    public void readBlock(org.apache.hadoop.thriftfs.api.RequestContext ctx, Block block, long offset, int length, org.apache.thrift.async.AsyncMethodCallback<AsyncClient.readBlock_call> resultHandler) throws org.apache.thrift.TException;

  }

  public static class Client extends org.apache.thrift.TServiceClient implements Iface {
    public static class Factory implements org.apache.thrift.TServiceClientFactory<Client> {
      public Factory() {}
      public Client getClient(org.apache.thrift.protocol.TProtocol prot) {
        return new Client(prot);
      }
      public Client getClient(org.apache.thrift.protocol.TProtocol iprot, org.apache.thrift.protocol.TProtocol oprot) {
        return new Client(iprot, oprot);
      }
    }

    public Client(org.apache.thrift.protocol.TProtocol prot)
    {
      super(prot, prot);
    }

    public Client(org.apache.thrift.protocol.TProtocol iprot, org.apache.thrift.protocol.TProtocol oprot) {
      super(iprot, oprot);
    }

    public BlockData readBlock(org.apache.hadoop.thriftfs.api.RequestContext ctx, Block block, long offset, int length) throws org.apache.hadoop.thriftfs.api.IOException, org.apache.thrift.TException
    {
      send_readBlock(ctx, block, offset, length);
      return recv_readBlock();
    }

    public void send_readBlock(org.apache.hadoop.thriftfs.api.RequestContext ctx, Block block, long offset, int length) throws org.apache.thrift.TException
    {
      readBlock_args args = new readBlock_args();
      args.setCtx(ctx);
      args.setBlock(block);
      args.setOffset(offset);
      args.setLength(length);
      sendBase("readBlock", args);
    }

    public BlockData recv_readBlock() throws org.apache.hadoop.thriftfs.api.IOException, org.apache.thrift.TException
    {
      readBlock_result result = new readBlock_result();
      receiveBase(result, "readBlock");
      if (result.isSetSuccess()) {
        return result.success;
      }
      if (result.err != null) {
        throw result.err;
      }
      throw new org.apache.thrift.TApplicationException(org.apache.thrift.TApplicationException.MISSING_RESULT, "readBlock failed: unknown result");
    }

  }
  public static class AsyncClient extends org.apache.thrift.async.TAsyncClient implements AsyncIface {
    public static class Factory implements org.apache.thrift.async.TAsyncClientFactory<AsyncClient> {
      private org.apache.thrift.async.TAsyncClientManager clientManager;
      private org.apache.thrift.protocol.TProtocolFactory protocolFactory;
      public Factory(org.apache.thrift.async.TAsyncClientManager clientManager, org.apache.thrift.protocol.TProtocolFactory protocolFactory) {
        this.clientManager = clientManager;
        this.protocolFactory = protocolFactory;
      }
      public AsyncClient getAsyncClient(org.apache.thrift.transport.TNonblockingTransport transport) {
        return new AsyncClient(protocolFactory, clientManager, transport);
      }
    }

    public AsyncClient(org.apache.thrift.protocol.TProtocolFactory protocolFactory, org.apache.thrift.async.TAsyncClientManager clientManager, org.apache.thrift.transport.TNonblockingTransport transport) {
      super(protocolFactory, clientManager, transport);
    }

    public void readBlock(org.apache.hadoop.thriftfs.api.RequestContext ctx, Block block, long offset, int length, org.apache.thrift.async.AsyncMethodCallback<readBlock_call> resultHandler) throws org.apache.thrift.TException {
      checkReady();
      readBlock_call method_call = new readBlock_call(ctx, block, offset, length, resultHandler, this, ___protocolFactory, ___transport);
      this.___currentMethod = method_call;
      ___manager.call(method_call);
    }

    public static class readBlock_call extends org.apache.thrift.async.TAsyncMethodCall {
      private org.apache.hadoop.thriftfs.api.RequestContext ctx;
      private Block block;
      private long offset;
      private int length;
      public readBlock_call(org.apache.hadoop.thriftfs.api.RequestContext ctx, Block block, long offset, int length, org.apache.thrift.async.AsyncMethodCallback<readBlock_call> resultHandler, org.apache.thrift.async.TAsyncClient client, org.apache.thrift.protocol.TProtocolFactory protocolFactory, org.apache.thrift.transport.TNonblockingTransport transport) throws org.apache.thrift.TException {
        super(client, protocolFactory, transport, resultHandler, false);
        this.ctx = ctx;
        this.block = block;
        this.offset = offset;
        this.length = length;
      }

      public void write_args(org.apache.thrift.protocol.TProtocol prot) throws org.apache.thrift.TException {
        prot.writeMessageBegin(new org.apache.thrift.protocol.TMessage("readBlock", org.apache.thrift.protocol.TMessageType.CALL, 0));
        readBlock_args args = new readBlock_args();
        args.setCtx(ctx);
        args.setBlock(block);
        args.setOffset(offset);
        args.setLength(length);
        args.write(prot);
        prot.writeMessageEnd();
      }

      public BlockData getResult() throws org.apache.hadoop.thriftfs.api.IOException, org.apache.thrift.TException {
        if (getState() != org.apache.thrift.async.TAsyncMethodCall.State.RESPONSE_READ) {
          throw new IllegalStateException("Method call not finished!");
        }
        org.apache.thrift.transport.TMemoryInputTransport memoryTransport = new org.apache.thrift.transport.TMemoryInputTransport(getFrameBuffer().array());
        org.apache.thrift.protocol.TProtocol prot = client.getProtocolFactory().getProtocol(memoryTransport);
        return (new Client(prot)).recv_readBlock();
      }
    }

  }

  public static class Processor<I extends Iface> extends org.apache.thrift.TBaseProcessor implements org.apache.thrift.TProcessor {
    private static final Logger LOGGER = LoggerFactory.getLogger(Processor.class.getName());
    public Processor(I iface) {
      super(iface, getProcessMap(new HashMap<String, org.apache.thrift.ProcessFunction<I, ? extends org.apache.thrift.TBase>>()));
    }

    protected Processor(I iface, Map<String,  org.apache.thrift.ProcessFunction<I, ? extends  org.apache.thrift.TBase>> processMap) {
      super(iface, getProcessMap(processMap));
    }

    private static <I extends Iface> Map<String,  org.apache.thrift.ProcessFunction<I, ? extends  org.apache.thrift.TBase>> getProcessMap(Map<String,  org.apache.thrift.ProcessFunction<I, ? extends  org.apache.thrift.TBase>> processMap) {
      processMap.put("readBlock", new readBlock());
      return processMap;
    }

    private static class readBlock<I extends Iface> extends org.apache.thrift.ProcessFunction<I, readBlock_args> {
      public readBlock() {
        super("readBlock");
      }

      protected readBlock_args getEmptyArgsInstance() {
        return new readBlock_args();
      }

      protected readBlock_result getResult(I iface, readBlock_args args) throws org.apache.thrift.TException {
        readBlock_result result = new readBlock_result();
        try {
          result.success = iface.readBlock(args.ctx, args.block, args.offset, args.length);
        } catch (org.apache.hadoop.thriftfs.api.IOException err) {
          result.err = err;
        }
        return result;
      }
    }

  }

  public static class readBlock_args implements org.apache.thrift.TBase<readBlock_args, readBlock_args._Fields>, java.io.Serializable, Cloneable   {
    private static final org.apache.thrift.protocol.TStruct STRUCT_DESC = new org.apache.thrift.protocol.TStruct("readBlock_args");

    private static final org.apache.thrift.protocol.TField CTX_FIELD_DESC = new org.apache.thrift.protocol.TField("ctx", org.apache.thrift.protocol.TType.STRUCT, (short)10);
    private static final org.apache.thrift.protocol.TField BLOCK_FIELD_DESC = new org.apache.thrift.protocol.TField("block", org.apache.thrift.protocol.TType.STRUCT, (short)1);
    private static final org.apache.thrift.protocol.TField OFFSET_FIELD_DESC = new org.apache.thrift.protocol.TField("offset", org.apache.thrift.protocol.TType.I64, (short)2);
    private static final org.apache.thrift.protocol.TField LENGTH_FIELD_DESC = new org.apache.thrift.protocol.TField("length", org.apache.thrift.protocol.TType.I32, (short)3);

    public org.apache.hadoop.thriftfs.api.RequestContext ctx; // required
    /**
     * Block to be read from.
     */
    public Block block; // required
    /**
     * Offset within the block where read must start from.
     */
    public long offset; // required
    /**
     * Number of bytes to read.
     */
    public int length; // required

    /** The set of fields this struct contains, along with convenience methods for finding and manipulating them. */
    public enum _Fields implements org.apache.thrift.TFieldIdEnum {
      CTX((short)10, "ctx"),
      /**
       * Block to be read from.
       */
      BLOCK((short)1, "block"),
      /**
       * Offset within the block where read must start from.
       */
      OFFSET((short)2, "offset"),
      /**
       * Number of bytes to read.
       */
      LENGTH((short)3, "length");

      private static final Map<String, _Fields> byName = new HashMap<String, _Fields>();

      static {
        for (_Fields field : EnumSet.allOf(_Fields.class)) {
          byName.put(field.getFieldName(), field);
        }
      }

      /**
       * Find the _Fields constant that matches fieldId, or null if its not found.
       */
      public static _Fields findByThriftId(int fieldId) {
        switch(fieldId) {
          case 10: // CTX
            return CTX;
          case 1: // BLOCK
            return BLOCK;
          case 2: // OFFSET
            return OFFSET;
          case 3: // LENGTH
            return LENGTH;
          default:
            return null;
        }
      }

      /**
       * Find the _Fields constant that matches fieldId, throwing an exception
       * if it is not found.
       */
      public static _Fields findByThriftIdOrThrow(int fieldId) {
        _Fields fields = findByThriftId(fieldId);
        if (fields == null) throw new IllegalArgumentException("Field " + fieldId + " doesn't exist!");
        return fields;
      }

      /**
       * Find the _Fields constant that matches name, or null if its not found.
       */
      public static _Fields findByName(String name) {
        return byName.get(name);
      }

      private final short _thriftId;
      private final String _fieldName;

      _Fields(short thriftId, String fieldName) {
        _thriftId = thriftId;
        _fieldName = fieldName;
      }

      public short getThriftFieldId() {
        return _thriftId;
      }

      public String getFieldName() {
        return _fieldName;
      }
    }

    // isset id assignments
    private static final int __OFFSET_ISSET_ID = 0;
    private static final int __LENGTH_ISSET_ID = 1;
    private BitSet __isset_bit_vector = new BitSet(2);

    public static final Map<_Fields, org.apache.thrift.meta_data.FieldMetaData> metaDataMap;
    static {
      Map<_Fields, org.apache.thrift.meta_data.FieldMetaData> tmpMap = new EnumMap<_Fields, org.apache.thrift.meta_data.FieldMetaData>(_Fields.class);
      tmpMap.put(_Fields.CTX, new org.apache.thrift.meta_data.FieldMetaData("ctx", org.apache.thrift.TFieldRequirementType.DEFAULT, 
          new org.apache.thrift.meta_data.StructMetaData(org.apache.thrift.protocol.TType.STRUCT, org.apache.hadoop.thriftfs.api.RequestContext.class)));
      tmpMap.put(_Fields.BLOCK, new org.apache.thrift.meta_data.FieldMetaData("block", org.apache.thrift.TFieldRequirementType.DEFAULT, 
          new org.apache.thrift.meta_data.StructMetaData(org.apache.thrift.protocol.TType.STRUCT, Block.class)));
      tmpMap.put(_Fields.OFFSET, new org.apache.thrift.meta_data.FieldMetaData("offset", org.apache.thrift.TFieldRequirementType.DEFAULT, 
          new org.apache.thrift.meta_data.FieldValueMetaData(org.apache.thrift.protocol.TType.I64)));
      tmpMap.put(_Fields.LENGTH, new org.apache.thrift.meta_data.FieldMetaData("length", org.apache.thrift.TFieldRequirementType.DEFAULT, 
          new org.apache.thrift.meta_data.FieldValueMetaData(org.apache.thrift.protocol.TType.I32)));
      metaDataMap = Collections.unmodifiableMap(tmpMap);
      org.apache.thrift.meta_data.FieldMetaData.addStructMetaDataMap(readBlock_args.class, metaDataMap);
    }

    public readBlock_args() {
    }

    public readBlock_args(
      org.apache.hadoop.thriftfs.api.RequestContext ctx,
      Block block,
      long offset,
      int length)
    {
      this();
      this.ctx = ctx;
      this.block = block;
      this.offset = offset;
      setOffsetIsSet(true);
      this.length = length;
      setLengthIsSet(true);
    }

    /**
     * Performs a deep copy on <i>other</i>.
     */
    public readBlock_args(readBlock_args other) {
      __isset_bit_vector.clear();
      __isset_bit_vector.or(other.__isset_bit_vector);
      if (other.isSetCtx()) {
        this.ctx = new org.apache.hadoop.thriftfs.api.RequestContext(other.ctx);
      }
      if (other.isSetBlock()) {
        this.block = new Block(other.block);
      }
      this.offset = other.offset;
      this.length = other.length;
    }

    public readBlock_args deepCopy() {
      return new readBlock_args(this);
    }

    @Override
    public void clear() {
      this.ctx = null;
      this.block = null;
      setOffsetIsSet(false);
      this.offset = 0;
      setLengthIsSet(false);
      this.length = 0;
    }

    public org.apache.hadoop.thriftfs.api.RequestContext getCtx() {
      return this.ctx;
    }

    public readBlock_args setCtx(org.apache.hadoop.thriftfs.api.RequestContext ctx) {
      this.ctx = ctx;
      return this;
    }

    public void unsetCtx() {
      this.ctx = null;
    }

    /** Returns true if field ctx is set (has been assigned a value) and false otherwise */
    public boolean isSetCtx() {
      return this.ctx != null;
    }

    public void setCtxIsSet(boolean value) {
      if (!value) {
        this.ctx = null;
      }
    }

    /**
     * Block to be read from.
     */
    public Block getBlock() {
      return this.block;
    }

    /**
     * Block to be read from.
     */
    public readBlock_args setBlock(Block block) {
      this.block = block;
      return this;
    }

    public void unsetBlock() {
      this.block = null;
    }

    /** Returns true if field block is set (has been assigned a value) and false otherwise */
    public boolean isSetBlock() {
      return this.block != null;
    }

    public void setBlockIsSet(boolean value) {
      if (!value) {
        this.block = null;
      }
    }

    /**
     * Offset within the block where read must start from.
     */
    public long getOffset() {
      return this.offset;
    }

    /**
     * Offset within the block where read must start from.
     */
    public readBlock_args setOffset(long offset) {
      this.offset = offset;
      setOffsetIsSet(true);
      return this;
    }

    public void unsetOffset() {
      __isset_bit_vector.clear(__OFFSET_ISSET_ID);
    }

    /** Returns true if field offset is set (has been assigned a value) and false otherwise */
    public boolean isSetOffset() {
      return __isset_bit_vector.get(__OFFSET_ISSET_ID);
    }

    public void setOffsetIsSet(boolean value) {
      __isset_bit_vector.set(__OFFSET_ISSET_ID, value);
    }

    /**
     * Number of bytes to read.
     */
    public int getLength() {
      return this.length;
    }

    /**
     * Number of bytes to read.
     */
    public readBlock_args setLength(int length) {
      this.length = length;
      setLengthIsSet(true);
      return this;
    }

    public void unsetLength() {
      __isset_bit_vector.clear(__LENGTH_ISSET_ID);
    }

    /** Returns true if field length is set (has been assigned a value) and false otherwise */
    public boolean isSetLength() {
      return __isset_bit_vector.get(__LENGTH_ISSET_ID);
    }

    public void setLengthIsSet(boolean value) {
      __isset_bit_vector.set(__LENGTH_ISSET_ID, value);
    }

    public void setFieldValue(_Fields field, Object value) {
      switch (field) {
      case CTX:
        if (value == null) {
          unsetCtx();
        } else {
          setCtx((org.apache.hadoop.thriftfs.api.RequestContext)value);
        }
        break;

      case BLOCK:
        if (value == null) {
          unsetBlock();
        } else {
          setBlock((Block)value);
        }
        break;

      case OFFSET:
        if (value == null) {
          unsetOffset();
        } else {
          setOffset((Long)value);
        }
        break;

      case LENGTH:
        if (value == null) {
          unsetLength();
        } else {
          setLength((Integer)value);
        }
        break;

      }
    }

    public Object getFieldValue(_Fields field) {
      switch (field) {
      case CTX:
        return getCtx();

      case BLOCK:
        return getBlock();

      case OFFSET:
        return Long.valueOf(getOffset());

      case LENGTH:
        return Integer.valueOf(getLength());

      }
      throw new IllegalStateException();
    }

    /** Returns true if field corresponding to fieldID is set (has been assigned a value) and false otherwise */
    public boolean isSet(_Fields field) {
      if (field == null) {
        throw new IllegalArgumentException();
      }

      switch (field) {
      case CTX:
        return isSetCtx();
      case BLOCK:
        return isSetBlock();
      case OFFSET:
        return isSetOffset();
      case LENGTH:
        return isSetLength();
      }
      throw new IllegalStateException();
    }

    @Override
    public boolean equals(Object that) {
      if (that == null)
        return false;
      if (that instanceof readBlock_args)
        return this.equals((readBlock_args)that);
      return false;
    }

    public boolean equals(readBlock_args that) {
      if (that == null)
        return false;

      boolean this_present_ctx = true && this.isSetCtx();
      boolean that_present_ctx = true && that.isSetCtx();
      if (this_present_ctx || that_present_ctx) {
        if (!(this_present_ctx && that_present_ctx))
          return false;
        if (!this.ctx.equals(that.ctx))
          return false;
      }

      boolean this_present_block = true && this.isSetBlock();
      boolean that_present_block = true && that.isSetBlock();
      if (this_present_block || that_present_block) {
        if (!(this_present_block && that_present_block))
          return false;
        if (!this.block.equals(that.block))
          return false;
      }

      boolean this_present_offset = true;
      boolean that_present_offset = true;
      if (this_present_offset || that_present_offset) {
        if (!(this_present_offset && that_present_offset))
          return false;
        if (this.offset != that.offset)
          return false;
      }

      boolean this_present_length = true;
      boolean that_present_length = true;
      if (this_present_length || that_present_length) {
        if (!(this_present_length && that_present_length))
          return false;
        if (this.length != that.length)
          return false;
      }

      return true;
    }

    @Override
    public int hashCode() {
      return 0;
    }

    public int compareTo(readBlock_args other) {
      if (!getClass().equals(other.getClass())) {
        return getClass().getName().compareTo(other.getClass().getName());
      }

      int lastComparison = 0;
      readBlock_args typedOther = (readBlock_args)other;

      lastComparison = Boolean.valueOf(isSetCtx()).compareTo(typedOther.isSetCtx());
      if (lastComparison != 0) {
        return lastComparison;
      }
      if (isSetCtx()) {
        lastComparison = org.apache.thrift.TBaseHelper.compareTo(this.ctx, typedOther.ctx);
        if (lastComparison != 0) {
          return lastComparison;
        }
      }
      lastComparison = Boolean.valueOf(isSetBlock()).compareTo(typedOther.isSetBlock());
      if (lastComparison != 0) {
        return lastComparison;
      }
      if (isSetBlock()) {
        lastComparison = org.apache.thrift.TBaseHelper.compareTo(this.block, typedOther.block);
        if (lastComparison != 0) {
          return lastComparison;
        }
      }
      lastComparison = Boolean.valueOf(isSetOffset()).compareTo(typedOther.isSetOffset());
      if (lastComparison != 0) {
        return lastComparison;
      }
      if (isSetOffset()) {
        lastComparison = org.apache.thrift.TBaseHelper.compareTo(this.offset, typedOther.offset);
        if (lastComparison != 0) {
          return lastComparison;
        }
      }
      lastComparison = Boolean.valueOf(isSetLength()).compareTo(typedOther.isSetLength());
      if (lastComparison != 0) {
        return lastComparison;
      }
      if (isSetLength()) {
        lastComparison = org.apache.thrift.TBaseHelper.compareTo(this.length, typedOther.length);
        if (lastComparison != 0) {
          return lastComparison;
        }
      }
      return 0;
    }

    public _Fields fieldForId(int fieldId) {
      return _Fields.findByThriftId(fieldId);
    }

    public void read(org.apache.thrift.protocol.TProtocol iprot) throws org.apache.thrift.TException {
      org.apache.thrift.protocol.TField field;
      iprot.readStructBegin();
      while (true)
      {
        field = iprot.readFieldBegin();
        if (field.type == org.apache.thrift.protocol.TType.STOP) { 
          break;
        }
        switch (field.id) {
          case 10: // CTX
            if (field.type == org.apache.thrift.protocol.TType.STRUCT) {
              this.ctx = new org.apache.hadoop.thriftfs.api.RequestContext();
              this.ctx.read(iprot);
            } else { 
              org.apache.thrift.protocol.TProtocolUtil.skip(iprot, field.type);
            }
            break;
          case 1: // BLOCK
            if (field.type == org.apache.thrift.protocol.TType.STRUCT) {
              this.block = new Block();
              this.block.read(iprot);
            } else { 
              org.apache.thrift.protocol.TProtocolUtil.skip(iprot, field.type);
            }
            break;
          case 2: // OFFSET
            if (field.type == org.apache.thrift.protocol.TType.I64) {
              this.offset = iprot.readI64();
              setOffsetIsSet(true);
            } else { 
              org.apache.thrift.protocol.TProtocolUtil.skip(iprot, field.type);
            }
            break;
          case 3: // LENGTH
            if (field.type == org.apache.thrift.protocol.TType.I32) {
              this.length = iprot.readI32();
              setLengthIsSet(true);
            } else { 
              org.apache.thrift.protocol.TProtocolUtil.skip(iprot, field.type);
            }
            break;
          default:
            org.apache.thrift.protocol.TProtocolUtil.skip(iprot, field.type);
        }
        iprot.readFieldEnd();
      }
      iprot.readStructEnd();

      // check for required fields of primitive type, which can't be checked in the validate method
      validate();
    }

    public void write(org.apache.thrift.protocol.TProtocol oprot) throws org.apache.thrift.TException {
      validate();

      oprot.writeStructBegin(STRUCT_DESC);
      if (this.block != null) {
        oprot.writeFieldBegin(BLOCK_FIELD_DESC);
        this.block.write(oprot);
        oprot.writeFieldEnd();
      }
      oprot.writeFieldBegin(OFFSET_FIELD_DESC);
      oprot.writeI64(this.offset);
      oprot.writeFieldEnd();
      oprot.writeFieldBegin(LENGTH_FIELD_DESC);
      oprot.writeI32(this.length);
      oprot.writeFieldEnd();
      if (this.ctx != null) {
        oprot.writeFieldBegin(CTX_FIELD_DESC);
        this.ctx.write(oprot);
        oprot.writeFieldEnd();
      }
      oprot.writeFieldStop();
      oprot.writeStructEnd();
    }

    @Override
    public String toString() {
      StringBuilder sb = new StringBuilder("readBlock_args(");
      boolean first = true;

      sb.append("ctx:");
      if (this.ctx == null) {
        sb.append("null");
      } else {
        sb.append(this.ctx);
      }
      first = false;
      if (!first) sb.append(", ");
      sb.append("block:");
      if (this.block == null) {
        sb.append("null");
      } else {
        sb.append(this.block);
      }
      first = false;
      if (!first) sb.append(", ");
      sb.append("offset:");
      sb.append(this.offset);
      first = false;
      if (!first) sb.append(", ");
      sb.append("length:");
      sb.append(this.length);
      first = false;
      sb.append(")");
      return sb.toString();
    }

    public void validate() throws org.apache.thrift.TException {
      // check for required fields
    }

    private void writeObject(java.io.ObjectOutputStream out) throws java.io.IOException {
      try {
        write(new org.apache.thrift.protocol.TCompactProtocol(new org.apache.thrift.transport.TIOStreamTransport(out)));
      } catch (org.apache.thrift.TException te) {
        throw new java.io.IOException(te);
      }
    }

    private void readObject(java.io.ObjectInputStream in) throws java.io.IOException, ClassNotFoundException {
      try {
        // it doesn't seem like you should have to do this, but java serialization is wacky, and doesn't call the default constructor.
        __isset_bit_vector = new BitSet(1);
        read(new org.apache.thrift.protocol.TCompactProtocol(new org.apache.thrift.transport.TIOStreamTransport(in)));
      } catch (org.apache.thrift.TException te) {
        throw new java.io.IOException(te);
      }
    }

  }

  public static class readBlock_result implements org.apache.thrift.TBase<readBlock_result, readBlock_result._Fields>, java.io.Serializable, Cloneable   {
    private static final org.apache.thrift.protocol.TStruct STRUCT_DESC = new org.apache.thrift.protocol.TStruct("readBlock_result");

    private static final org.apache.thrift.protocol.TField SUCCESS_FIELD_DESC = new org.apache.thrift.protocol.TField("success", org.apache.thrift.protocol.TType.STRUCT, (short)0);
    private static final org.apache.thrift.protocol.TField ERR_FIELD_DESC = new org.apache.thrift.protocol.TField("err", org.apache.thrift.protocol.TType.STRUCT, (short)1);

    public BlockData success; // required
    public org.apache.hadoop.thriftfs.api.IOException err; // required

    /** The set of fields this struct contains, along with convenience methods for finding and manipulating them. */
    public enum _Fields implements org.apache.thrift.TFieldIdEnum {
      SUCCESS((short)0, "success"),
      ERR((short)1, "err");

      private static final Map<String, _Fields> byName = new HashMap<String, _Fields>();

      static {
        for (_Fields field : EnumSet.allOf(_Fields.class)) {
          byName.put(field.getFieldName(), field);
        }
      }

      /**
       * Find the _Fields constant that matches fieldId, or null if its not found.
       */
      public static _Fields findByThriftId(int fieldId) {
        switch(fieldId) {
          case 0: // SUCCESS
            return SUCCESS;
          case 1: // ERR
            return ERR;
          default:
            return null;
        }
      }

      /**
       * Find the _Fields constant that matches fieldId, throwing an exception
       * if it is not found.
       */
      public static _Fields findByThriftIdOrThrow(int fieldId) {
        _Fields fields = findByThriftId(fieldId);
        if (fields == null) throw new IllegalArgumentException("Field " + fieldId + " doesn't exist!");
        return fields;
      }

      /**
       * Find the _Fields constant that matches name, or null if its not found.
       */
      public static _Fields findByName(String name) {
        return byName.get(name);
      }

      private final short _thriftId;
      private final String _fieldName;

      _Fields(short thriftId, String fieldName) {
        _thriftId = thriftId;
        _fieldName = fieldName;
      }

      public short getThriftFieldId() {
        return _thriftId;
      }

      public String getFieldName() {
        return _fieldName;
      }
    }

    // isset id assignments

    public static final Map<_Fields, org.apache.thrift.meta_data.FieldMetaData> metaDataMap;
    static {
      Map<_Fields, org.apache.thrift.meta_data.FieldMetaData> tmpMap = new EnumMap<_Fields, org.apache.thrift.meta_data.FieldMetaData>(_Fields.class);
      tmpMap.put(_Fields.SUCCESS, new org.apache.thrift.meta_data.FieldMetaData("success", org.apache.thrift.TFieldRequirementType.DEFAULT, 
          new org.apache.thrift.meta_data.StructMetaData(org.apache.thrift.protocol.TType.STRUCT, BlockData.class)));
      tmpMap.put(_Fields.ERR, new org.apache.thrift.meta_data.FieldMetaData("err", org.apache.thrift.TFieldRequirementType.DEFAULT, 
          new org.apache.thrift.meta_data.FieldValueMetaData(org.apache.thrift.protocol.TType.STRUCT)));
      metaDataMap = Collections.unmodifiableMap(tmpMap);
      org.apache.thrift.meta_data.FieldMetaData.addStructMetaDataMap(readBlock_result.class, metaDataMap);
    }

    public readBlock_result() {
    }

    public readBlock_result(
      BlockData success,
      org.apache.hadoop.thriftfs.api.IOException err)
    {
      this();
      this.success = success;
      this.err = err;
    }

    /**
     * Performs a deep copy on <i>other</i>.
     */
    public readBlock_result(readBlock_result other) {
      if (other.isSetSuccess()) {
        this.success = new BlockData(other.success);
      }
      if (other.isSetErr()) {
        this.err = new org.apache.hadoop.thriftfs.api.IOException(other.err);
      }
    }

    public readBlock_result deepCopy() {
      return new readBlock_result(this);
    }

    @Override
    public void clear() {
      this.success = null;
      this.err = null;
    }

    public BlockData getSuccess() {
      return this.success;
    }

    public readBlock_result setSuccess(BlockData success) {
      this.success = success;
      return this;
    }

    public void unsetSuccess() {
      this.success = null;
    }

    /** Returns true if field success is set (has been assigned a value) and false otherwise */
    public boolean isSetSuccess() {
      return this.success != null;
    }

    public void setSuccessIsSet(boolean value) {
      if (!value) {
        this.success = null;
      }
    }

    public org.apache.hadoop.thriftfs.api.IOException getErr() {
      return this.err;
    }

    public readBlock_result setErr(org.apache.hadoop.thriftfs.api.IOException err) {
      this.err = err;
      return this;
    }

    public void unsetErr() {
      this.err = null;
    }

    /** Returns true if field err is set (has been assigned a value) and false otherwise */
    public boolean isSetErr() {
      return this.err != null;
    }

    public void setErrIsSet(boolean value) {
      if (!value) {
        this.err = null;
      }
    }

    public void setFieldValue(_Fields field, Object value) {
      switch (field) {
      case SUCCESS:
        if (value == null) {
          unsetSuccess();
        } else {
          setSuccess((BlockData)value);
        }
        break;

      case ERR:
        if (value == null) {
          unsetErr();
        } else {
          setErr((org.apache.hadoop.thriftfs.api.IOException)value);
        }
        break;

      }
    }

    public Object getFieldValue(_Fields field) {
      switch (field) {
      case SUCCESS:
        return getSuccess();

      case ERR:
        return getErr();

      }
      throw new IllegalStateException();
    }

    /** Returns true if field corresponding to fieldID is set (has been assigned a value) and false otherwise */
    public boolean isSet(_Fields field) {
      if (field == null) {
        throw new IllegalArgumentException();
      }

      switch (field) {
      case SUCCESS:
        return isSetSuccess();
      case ERR:
        return isSetErr();
      }
      throw new IllegalStateException();
    }

    @Override
    public boolean equals(Object that) {
      if (that == null)
        return false;
      if (that instanceof readBlock_result)
        return this.equals((readBlock_result)that);
      return false;
    }

    public boolean equals(readBlock_result that) {
      if (that == null)
        return false;

      boolean this_present_success = true && this.isSetSuccess();
      boolean that_present_success = true && that.isSetSuccess();
      if (this_present_success || that_present_success) {
        if (!(this_present_success && that_present_success))
          return false;
        if (!this.success.equals(that.success))
          return false;
      }

      boolean this_present_err = true && this.isSetErr();
      boolean that_present_err = true && that.isSetErr();
      if (this_present_err || that_present_err) {
        if (!(this_present_err && that_present_err))
          return false;
        if (!this.err.equals(that.err))
          return false;
      }

      return true;
    }

    @Override
    public int hashCode() {
      return 0;
    }

    public int compareTo(readBlock_result other) {
      if (!getClass().equals(other.getClass())) {
        return getClass().getName().compareTo(other.getClass().getName());
      }

      int lastComparison = 0;
      readBlock_result typedOther = (readBlock_result)other;

      lastComparison = Boolean.valueOf(isSetSuccess()).compareTo(typedOther.isSetSuccess());
      if (lastComparison != 0) {
        return lastComparison;
      }
      if (isSetSuccess()) {
        lastComparison = org.apache.thrift.TBaseHelper.compareTo(this.success, typedOther.success);
        if (lastComparison != 0) {
          return lastComparison;
        }
      }
      lastComparison = Boolean.valueOf(isSetErr()).compareTo(typedOther.isSetErr());
      if (lastComparison != 0) {
        return lastComparison;
      }
      if (isSetErr()) {
        lastComparison = org.apache.thrift.TBaseHelper.compareTo(this.err, typedOther.err);
        if (lastComparison != 0) {
          return lastComparison;
        }
      }
      return 0;
    }

    public _Fields fieldForId(int fieldId) {
      return _Fields.findByThriftId(fieldId);
    }

    public void read(org.apache.thrift.protocol.TProtocol iprot) throws org.apache.thrift.TException {
      org.apache.thrift.protocol.TField field;
      iprot.readStructBegin();
      while (true)
      {
        field = iprot.readFieldBegin();
        if (field.type == org.apache.thrift.protocol.TType.STOP) { 
          break;
        }
        switch (field.id) {
          case 0: // SUCCESS
            if (field.type == org.apache.thrift.protocol.TType.STRUCT) {
              this.success = new BlockData();
              this.success.read(iprot);
            } else { 
              org.apache.thrift.protocol.TProtocolUtil.skip(iprot, field.type);
            }
            break;
          case 1: // ERR
            if (field.type == org.apache.thrift.protocol.TType.STRUCT) {
              this.err = new org.apache.hadoop.thriftfs.api.IOException();
              this.err.read(iprot);
            } else { 
              org.apache.thrift.protocol.TProtocolUtil.skip(iprot, field.type);
            }
            break;
          default:
            org.apache.thrift.protocol.TProtocolUtil.skip(iprot, field.type);
        }
        iprot.readFieldEnd();
      }
      iprot.readStructEnd();

      // check for required fields of primitive type, which can't be checked in the validate method
      validate();
    }

    public void write(org.apache.thrift.protocol.TProtocol oprot) throws org.apache.thrift.TException {
      oprot.writeStructBegin(STRUCT_DESC);

      if (this.isSetSuccess()) {
        oprot.writeFieldBegin(SUCCESS_FIELD_DESC);
        this.success.write(oprot);
        oprot.writeFieldEnd();
      } else if (this.isSetErr()) {
        oprot.writeFieldBegin(ERR_FIELD_DESC);
        this.err.write(oprot);
        oprot.writeFieldEnd();
      }
      oprot.writeFieldStop();
      oprot.writeStructEnd();
    }

    @Override
    public String toString() {
      StringBuilder sb = new StringBuilder("readBlock_result(");
      boolean first = true;

      sb.append("success:");
      if (this.success == null) {
        sb.append("null");
      } else {
        sb.append(this.success);
      }
      first = false;
      if (!first) sb.append(", ");
      sb.append("err:");
      if (this.err == null) {
        sb.append("null");
      } else {
        sb.append(this.err);
      }
      first = false;
      sb.append(")");
      return sb.toString();
    }

    public void validate() throws org.apache.thrift.TException {
      // check for required fields
    }

    private void writeObject(java.io.ObjectOutputStream out) throws java.io.IOException {
      try {
        write(new org.apache.thrift.protocol.TCompactProtocol(new org.apache.thrift.transport.TIOStreamTransport(out)));
      } catch (org.apache.thrift.TException te) {
        throw new java.io.IOException(te);
      }
    }

    private void readObject(java.io.ObjectInputStream in) throws java.io.IOException, ClassNotFoundException {
      try {
        read(new org.apache.thrift.protocol.TCompactProtocol(new org.apache.thrift.transport.TIOStreamTransport(in)));
      } catch (org.apache.thrift.TException te) {
        throw new java.io.IOException(te);
      }
    }

  }

}
