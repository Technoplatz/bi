import { Pipe, PipeTransform } from "@angular/core";

@Pipe({ name: "sort" })
export class ArraySortPipe implements PipeTransform {
  transform(array: any[], field: string): any[] {
    if (!Array.isArray(array)) {
      return array;
    }
    return [...array].sort((a: any, b: any) => (a[field] < b[field] ? -1 : a[field] > b[field] ? 1 : 0));
  }
}
